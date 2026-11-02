"""Validated optional board data for Daily Puzzle Hub.

The daily answer updater remains the authority for whether a puzzle is verified.
We never infer Queens region colours from queen coordinates.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from datetime import date

NEIGHBOURS = [(r, c) for r in (-1,0,1) for c in (-1,0,1) if (r or c)]


def valid_strands(grid, paths, answer):
    if (not isinstance(grid,list) or len(grid)!=8 or
        any(not isinstance(row,list) or len(row)!=6 or any(not isinstance(x,str) or not re.fullmatch('[A-Z]',x) for x in row) for row in grid)):
        return False
    if not isinstance(paths,dict):return False
    words=[str(w).upper() for w in answer.get('words',[])] + [str(answer.get('spangram','')).upper()]
    if len(set(words))!=len(words) or set(paths)!=set(words):return False
    used=set()
    for word in words:
        p=paths.get(word)
        if not isinstance(p,list) or len(p)!=len(word):return False
        spelling=''
        previous=None
        for pos in p:
            if not isinstance(pos,list) or len(pos)!=2:return False
            r,c=pos
            if type(r)!=int or type(c)!=int or not 1<=r<=8 or not 1<=c<=6 or (r,c) in used:return False
            if previous and max(abs(previous[0]-r),abs(previous[1]-c))!=1:return False
            used.add((r,c));spelling+=grid[r-1][c-1];previous=(r,c)
        if spelling!=word:return False
    if len(used)!=48:return False
    span=paths[words[-1]]
    rset={r for r,c in span};cset={c for r,c in span}
    return (1 in rset and 8 in rset) or (1 in cset and 6 in cset)


def valid_queens_regions(regions, cols):
    n=len(cols)
    if (not isinstance(regions,list) or len(regions)!=n or
        any(not isinstance(row,list) or len(row)!=n for row in regions)):
        return False
    labels={str(x) for row in regions for x in row}
    if len(labels)!=n:return False
    queen_labels=[]
    for r,col in enumerate(cols):
        if type(col)!=int or not 1<=col<=n:return False
        queen_labels.append(str(regions[r][col-1]))
    return len(set(queen_labels))==n


def find_strands_board(text):
    """Use only a dated source's explicit 48-letter board; no synthesized grid."""
    if not text:return None
    candidates=[r'\bThe board\b\s*(.*?)\s*\bThe answers\b',
                r'\bThe board\b\s*(.*?)\s*\bSpangram\b',
                r'\bToday.s letter board\b\s*(.*?)\s*\bToday.s Strands answers\b']
    for patt in candidates:
        m=re.search(patt,text,re.I|re.S)
        if not m:continue
        letters=re.findall(r'\b[A-Z]\b',m.group(1).upper())
        if len(letters)==48:
            return [letters[r*6:(r+1)*6] for r in range(8)]
    return None


def find_unique_paths(grid,answer):
    """Only publish automatically derived word routes when the exact cover is unique."""
    words=list(answer.get('words',[]))+[answer.get('spangram','')]
    words=[str(w).upper() for w in words]
    if not grid or len(set(words))!=len(words) or sum(map(len,words))!=48:return None
    candidates={}
    for word in words:
        paths=[]
        def explore(r,c,i,used,path):
            if len(paths)>1000:return
            if i==len(word):paths.append(tuple(path));return
            for dr,dc in NEIGHBOURS:
                nr,nc=r+dr,c+dc
                ix=nr*6+nc
                if 0<=nr<8 and 0<=nc<6 and grid[nr][nc]==word[i] and not used>>ix&1:
                    explore(nr,nc,i+1,used|(1<<ix),path+[ix])
        for r in range(8):
            for c in range(6):
                if grid[r][c]==word[0]:explore(r,c,1,1<<(r*6+c),[r*6+c])
        if not paths or len(paths)>1000:return None
        if word==answer.get('spangram','').upper():
            paths=[p for p in paths if (any(q//6==0 for q in p) and any(q//6==7 for q in p)) or (any(q%6==0 for q in p) and any(q%6==5 for q in p))]
        if not paths:return None
        candidates[word]=[(p,sum(1<<v for v in p)) for p in paths]
    results=[]
    def search(remaining,mask,selected):
        if len(results)>=2:return
        if not remaining:
            if mask.bit_count()==48:results.append(selected.copy())
            return
        word=min(remaining,key=lambda w:len(candidates[w]))
        for path,bits in candidates[word]:
            if bits&mask:continue
            selected[word]=[[k//6+1,k%6+1] for k in path]
            search(remaining-{word},mask|bits,selected)
            del selected[word]
            if len(results)>=2:return
    search(set(words),0,{})
    if len(results)!=1:return None
    return results[0] if valid_strands(grid,results[0],answer) else None


def enrich_daily_boards(day, data, root, fetch=None):
    """Attach verified richer boards to an already-verified day's answer data."""
    daystr=day.isoformat()
    board_file=Path(root)/'data'/'boards'/f'{daystr}.json'
    external={}
    if board_file.exists():
        try:external=json.loads(board_file.read_text(encoding='utf-8'))
        except (ValueError, OSError):pass
    previous={}
    prev_file=Path(root)/'data'/f'{daystr}.json'
    if prev_file.exists():
        try:
            old=json.loads(prev_file.read_text(encoding='utf-8'))
            if old.get('date')==daystr:previous=old.get('games',{})
        except (ValueError,OSError):pass
    for game in ('strands','queens'):
        entry=data.get('games',{}).get(game)
        if not entry or entry.get('status')!='verified':continue
        answer=entry.get('answer') or {}
        archived=(previous.get(game) or {}).get('answer') or {}
        curated=external.get(game) or {}
        if game=='strands':
            grid=curated.get('grid')
            paths=curated.get('paths')
            if not valid_strands(grid,paths,answer):
                grid,paths=archived.get('grid'),archived.get('paths')
            if valid_strands(grid,paths,answer):
                answer['grid'],answer['paths']=grid,paths
                print('  ✓ strands complete grid + paths')
                continue
            # Future puzzles: attempt board import, but never make up a path.
            if callable(fetch):
                slug=day.strftime('%B').lower()+'-'+str(day.day)+'-'+str(day.year)
                url=f'https://walkthroughs.net/strands-answers/{slug}'
                page=fetch(url)
                if day.strftime('%B').lower() in page.lower() and str(day.year) in page:
                    grid=find_strands_board(re.sub('<[^>]+>',' ',page))
                    if grid:
                        paths=find_unique_paths(grid,answer)
                        if paths and valid_strands(grid,paths,answer):
                            answer['grid'],answer['paths']=grid,paths
                            print('  ✓ strands grid + uniquely reconstructed paths')
                        else:
                            answer['grid']=grid
                            print('  ~ strands board found; paths not uniquely verified')
        else:
            regions=curated.get('regions')
            if not valid_queens_regions(regions,answer.get('cols',[])):
                regions=archived.get('regions')
            if valid_queens_regions(regions,answer.get('cols',[])):
                answer['regions']=regions
                print('  ✓ queens region map validated')
            else:
                print('  ~ queens full region map unavailable; placements retained')
    for game,clues in (external.get('clues') or {}).items():
        entry=data.get('games',{}).get(game)
        if entry and entry.get('status')=='verified' and isinstance(clues,list):
            entry['clues']=[str(x) for x in clues[:4] if isinstance(x,str) and x.strip()]
