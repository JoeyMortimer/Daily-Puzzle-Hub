"""Validate solutions before publishing them as verified."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SUPPORTED={'word','strands','words','ladder','queens','tango','zip','sudoku','patches','sumplete','math','notice'}

def validate(game_id,entry):
    a=entry.get('answer')
    if entry.get('status')!='verified':return
    assert a and a.get('type') in SUPPORTED,(game_id,'bad type')
    t=a['type']
    if t=='word':assert a['value'] and isinstance(a['value'],str)
    if t=='strands':assert len(a['spangram'])>=4 and 3<=len(a['words'])<=12
    if t=='words':assert 3<=len(a['words'])<=8
    if t=='ladder':
        words=a['words'];assert len(words)==7
        assert all(len(x)==len(words[0]) for x in words)
        assert all(sum(c!=d for c,d in zip(words[i],words[i+1]))==1 for i in range(len(words)-1))
    if t=='queens':
        cols=a['cols'];n=len(cols)
        assert set(cols)==set(range(1,n+1)) and all(abs(cols[i]-cols[i-1])>1 for i in range(1,n))
    if t=='tango':
        rows=a['rows'];assert len(rows)==6 and all(len(r)==6 and r.count('S')==3 and r.count('M')==3 for r in rows)
        assert all([r[c] for r in rows].count('S')==3 for c in range(6))
        assert all(not(rows[r][c]==rows[r][c+1]==rows[r][c+2]) for r in range(6) for c in range(4))
        assert all(not(rows[r][c]==rows[r+1][c]==rows[r+2][c]) for r in range(4) for c in range(6))
    if t=='zip':
        path=a['path'];n=len(path);side=int(n**0.5)
        assert side in (6,7,8,9) and n==side*side and len({tuple(p) for p in path})==n
        assert all(1<=r<=side and 1<=c<=side for r,c in path)
        assert all(abs(path[i][0]-path[i-1][0])+abs(path[i][1]-path[i-1][1])==1 for i in range(1,n))
    if t=='sudoku':
        rows=a['rows'];digits=set(range(1,7))
        assert len(rows)==6 and all(set(r)==digits for r in rows)
        assert all({r[c] for r in rows}==digits for c in range(6))
        assert all({rows[r][c] for r in range(br,br+2) for c in range(bc,bc+3)}==digits for br in range(0,6,2) for bc in range(0,6,3))
    if t=='patches':
        occupied=[]
        side=max(max(r2,c2) for _,_,r2,c2 in a['rects'])
        assert side in (6,7,8,9)
        for r1,c1,r2,c2 in a['rects']:
            assert 1<=r1<=r2<=side and 1<=c1<=c2<=side
            occupied.extend((r,c) for r in range(r1,r2+1) for c in range(c1,c2+1))
        assert len(occupied)==len(set(occupied))==side*side
    if t=='sumplete':
        grid=a['grid'];kept=a['kept'];rt=a['rowTargets'];ct=a['colTargets']
        assert len(grid)==len(kept)==len(rt)==len(ct)==5
        assert all(len(row)==5 for row in grid+kept)
        assert all(sum(grid[r][c]*kept[r][c] for c in range(5))==rt[r] for r in range(5))
        assert all(sum(grid[r][c]*kept[r][c] for r in range(5))==ct[c] for c in range(5))

for file in sorted((ROOT/'data').glob('????-??-??.json')):
    data=json.loads(file.read_text())
    assert data['date']==file.stem
    assert set(data['games'])=={'wordle','strands','crosswordle','mathler','sumplete','pinpoint','crossclimb','queens','tango','zip','mini-sudoku','patches','wend'}
    for game,entry in data['games'].items():validate(game,entry)
    print(file.name,'OK',sum(e.get('status')=='verified' for e in data['games'].values()),'verified')
