#!/usr/bin/env python3
"""Patch Daily Puzzle Hub's Zip, Patches, and Strands handling.
Run from repository root. Preserves daily answer files.
"""
from pathlib import Path
import ast
import re

ROOT=Path.cwd()
u=ROOT/'scripts/update.py'
v=ROOT/'scripts/validate.py'
j=ROOT/'app.js'
for p in [u,v,j]:
    if not p.is_file():
        raise SystemExit(f'Expected {p}. Run from the Daily-Puzzle-Hub folder.')

def change(text,old,new,label):
    if old in text:
        print('Updating:',label)
        return text.replace(old,new,1)
    if new in text:
        print('Already updated:',label)
        return text
    raise SystemExit(f'Unexpected file version, stopping safely at: {label}. No files saved.')

up=u.read_text(encoding='utf-8')
up=change(up,"    # Website renderer currently supports 8x8. Smaller boards should remain unavailable.\n    return {'type':'zip','path':path} if side==8 else None", "    # Render every valid 6x6 to 9x9 board.\n    return {'type':'zip','path':path}", 'Zip sizes')
up=change(up,"""    cells=[]
    for r1,c1,r2,c2 in rectangles:
        if not (1<=r1<=r2<=8 and 1<=c1<=c2<=8):return None
        cells.extend((r,c) for r in range(r1,r2+1) for c in range(c1,c2+1))
    if len(cells)!=64 or len(set(cells))!=64:return None""", """    cells=[]
    side=max(max(r2,c2) for _,_,r2,c2 in rectangles)
    if side not in (6,7,8,9):return None
    for r1,c1,r2,c2 in rectangles:
        if not (1<=r1<=r2<=side and 1<=c1<=c2<=side):return None
        cells.extend((r,c) for r in range(r1,r2+1) for c in range(c1,c2+1))
    if len(cells)!=side*side or len(set(cells))!=side*side:return None""", 'Patches sizes')
# Replace Strands' brittle one-line regex with labelled sections and a board-length check.
start=up.find('def update_strands(day,out):')
end=up.find('\ndef update(day,force=False):',start)
if start<0 or end<0:raise SystemExit('Cannot locate Strands updater; nothing saved.')
newstr='''def update_strands(day,out):
    slug=day.strftime('%B').lower()+'-'+str(day.day)+'-'+str(day.year)
    url=f'https://walkthroughs.net/strands-answers/{slug}'
    txt=checked_page(fetch(url),day,'Strands')
    if txt:
        theme=re.search(r'Theme\\s*[“\\"‘\\\']([^”\\"’\\\']+)[”\\"’\\\']',txt,re.I)
        section=re.split(r'\\bThe answers\\b',txt,maxsplit=1,flags=re.I)[-1]
        sp=re.search(r'\\bSpangram\\s+(?:Spangram\\s+)?([A-Z]{4,})\\b',section,re.I)
        wt=re.search(r'\\bTheme words\\s*\\((\\d+)\\)\\s*(.*)',section,re.I|re.S)
        if theme and sp and wt:
            count=int(wt.group(1))
            tail=re.split(r'\\b(?:How to play|Yesterday|More puzzles|Frequently asked questions)\\b',wt.group(2),maxsplit=1,flags=re.I)[0]
            words=re.findall(r'\\b[A-Z]{3,}\\b',tail)[:count]
            spangram=sp.group(1).upper()
            if 3<=count<=12 and len(words)==count and len(spangram)+sum(map(len,words))==48:
                out['games']['strands']={'status':'verified','number':f'#{973+(day-BASE).days}','hint':[],'answer':{'type':'strands','theme':theme.group(1),'spangram':spangram,'words':words},'source':url}
                print('  ✓ strands')
                return
        print('  - strands page fetched, but its solution failed extraction/validation')
    else:
        print('  - strands page missing or date mismatch')
    out['games']['strands']={'status':'missing','number':f'#{973+(day-BASE).days}','answer':None,'source':url}
    print('  - strands not confirmed')
'''
oldstr=up[start:end]
if 'The answers\\s+Spangram' in oldstr:
    up=up[:start]+newstr+up[end:]
    print('Updating: Strands extraction')
elif 'strands page fetched, but its solution' in oldstr:
    print('Already updated: Strands extraction')
else:
    raise SystemExit('Unexpected Strands code; nothing saved.')
ast.parse(up)

val=v.read_text(encoding='utf-8')
val=change(val,"""        path=a['path'];assert len(path)==64 and len({tuple(p) for p in path})==64
        assert all(1<=r<=8 and 1<=c<=8 for r,c in path)
        assert all(abs(path[i][0]-path[i-1][0])+abs(path[i][1]-path[i-1][1])==1 for i in range(1,64))""", """        path=a['path'];n=len(path);side=int(n**0.5)
        assert side in (6,7,8,9) and n==side*side and len({tuple(p) for p in path})==n
        assert all(1<=r<=side and 1<=c<=side for r,c in path)
        assert all(abs(path[i][0]-path[i-1][0])+abs(path[i][1]-path[i-1][1])==1 for i in range(1,n))""", 'Zip validator')
val=change(val,"""        occupied=[]
        for r1,c1,r2,c2 in a['rects']:
            assert 1<=r1<=r2<=8 and 1<=c1<=c2<=8
            occupied.extend((r,c) for r in range(r1,r2+1) for c in range(c1,c2+1))
        assert len(occupied)==len(set(occupied))==64""", """        occupied=[]
        side=max(max(r2,c2) for _,_,r2,c2 in a['rects'])
        assert side in (6,7,8,9)
        for r1,c1,r2,c2 in a['rects']:
            assert 1<=r1<=r2<=side and 1<=c1<=c2<=side
            occupied.extend((r,c) for r in range(r1,r2+1) for c in range(c1,c2+1))
        assert len(occupied)==len(set(occupied))==side*side""", 'Patches validator')
ast.parse(val)

js=j.read_text(encoding='utf-8')
js=change(js,"""const matrix=Array.from({length:8},()=>Array(8).fill(''));a.path.forEach""", """const side=Math.sqrt(a.path.length);const matrix=Array.from({length:side},()=>Array(side).fill(''));a.path.forEach""", 'Zip renderer grid')
js=change(js,"""v===1?'start':v===64?'end':''""", """v===1?'start':v===a.path.length?'end':''""", 'Zip renderer endpoints')
js=change(js,"""+'<p class="answer-desc">Numbers show the step order through all 64 cells. Start at 1, finish at 64.</p>'""", """+`<p class="answer-desc">Numbers show the step order through all ${a.path.length} cells. Start at 1, finish at ${a.path.length}.</p>`""", 'Zip renderer explanation')
js=change(js,"""const matrix=Array.from({length:8},()=>Array(8).fill(null));a.rects.forEach""", """const side=Math.max(...a.rects.map(rect=>Math.max(rect[2],rect[3])));const matrix=Array.from({length:side},()=>Array(side).fill(null));a.rects.forEach""", 'Patches renderer')

# Write only after all replacement checks and Python parsing succeed.
for p,s in [(u,up),(v,val),(j,js)]:
    p.write_text(s,encoding='utf-8')
    print('Saved',p.relative_to(ROOT))
print('Next: python scripts/validate.py')
