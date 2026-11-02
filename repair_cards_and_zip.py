#!/usr/bin/env python3
"""Daily Puzzle Hub: stop card stretching and render authentic Zip checkpoints.
Idempotent and guarded; run at the repository root.
"""
from pathlib import Path
import ast, json, re

root=Path.cwd()
required=[root/'style.css', root/'app.js',root/'index.html',root/'scripts/update.py']
if not all(x.is_file() for x in required):
    raise SystemExit('Run inside Daily-Puzzle-Hub root (where index.html and app.js live).')

js_file=root/'app.js'; css_file=root/'style.css'; html_file=root/'index.html'; py_file=root/'scripts/update.py'
js=js_file.read_text(encoding='utf-8'); css=css_file.read_text(encoding='utf-8')
html=html_file.read_text(encoding='utf-8'); py=py_file.read_text(encoding='utf-8')
MARK='DPH ZIP CHECKPOINTS V2'
ZIP_KNOWN_CHECKPOINTS={
 '2026-11-01':[(1,4,2),(2,7,2),(3,4,5),(4,2,2),(5,2,3),(6,3,5),(7,4,1),(8,8,2),(9,6,4),(10,5,8),(11,1,7),(12,2,7),(13,5,7),(14,7,7),(15,7,6),(16,5,4)],
 '2026-11-02':[(1,1,1),(2,1,4),(3,2,5),(4,3,5),(5,3,3),(6,1,3),(7,1,2),(8,4,2),(9,5,3),(10,4,5),(11,5,4)],
}

# ZIP: a.checkpoints is a validated list [number, row, column]. The route path
# remains cell-by-cell. No fabricated step counts appear in the numbered dots.
new_zip=r'''function dphZip(a){
 const path=Array.isArray(a.path)?a.path:[], side=Math.sqrt(path.length);
 if(!Number.isInteger(side)||side<3)return '<p class="answer-desc">Route data is incomplete.</p>';
 const markers=new Map(), positions=new Map();
 path.forEach(([r,c],i)=>positions.set(`${r},${c}`,i));
 let lastStep=-1,lastNum=0,valid=true;
 const entries=Array.isArray(a.checkpoints)?a.checkpoints:[];
 for(const row of entries){
   if(!Array.isArray(row)||row.length!==3){valid=false;break;}
   const [number,r,c]=row,step=positions.get(`${r},${c}`);
   if(!Number.isInteger(number)||number!==lastNum+1||step===undefined||step<=lastStep){valid=false;break;}
   markers.set(`${r},${c}`,number);lastNum=number;lastStep=step;
 }
 if(!valid||markers.size<2||lastStep!==path.length-1||positions.get(`${entries[0]?.[1]},${entries[0]?.[2]}`)!==0)markers.clear();
 const cells=Array.from({length:side},(_,r)=>Array.from({length:side},(_,c)=>{
   const mark=markers.get(`${r+1},${c+1}`),first=path[0][0]===r+1&&path[0][1]===c+1;
   const last=path[path.length-1][0]===r+1&&path[path.length-1][1]===c+1;
   const label=mark===undefined?'':String(mark);
   const title=mark!==undefined?`Checkpoint ${mark}`:(first?'Route start':last?'Route finish':'Path cell');
   return `<div class="board-cell ${first?'start':last?'end':''}" aria-label="${title}">${label?`<span>${label}</span>`:''}</div>`;
 }).join('')).join('');
 const points=path.map(([r,c])=>`${(c-.5)*100},${(r-.5)*100}`).join(' ');
 const [r0,c0]=path[0],[r1,c1]=path[path.length-1];
 const note=markers.size?`The numbered circles are the actual puzzle checkpoints (1–${lastNum}), not step counts. The green line visits all ${path.length} squares.`:`The green line visits all ${path.length} squares. Original numbered checkpoints have not been confirmed for this date, so none are invented.`;
 return `<div class="zip-path-wrap" role="img" aria-label="Solved Zip route with ${path.length} squares"><div class="game-board zip-board zip-line-board" style="grid-template-columns:repeat(${side},minmax(0,1fr))">${cells}</div><svg class="zip-route" viewBox="0 0 ${side*100} ${side*100}" preserveAspectRatio="none" aria-hidden="true"><polyline points="${points}" fill="none" stroke="#087c68" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/><circle cx="${(c0-.5)*100}" cy="${(r0-.5)*100}" r="22" fill="#27855c"/><circle cx="${(c1-.5)*100}" cy="${(r1-.5)*100}" r="22" fill="#3071b5"/></svg></div><p class="answer-desc">${note}</p>`;
}
'''
if 'function dphZip(a){' not in js or 'function dphWend(a){' not in js:
    raise SystemExit('Expected existing visual upgrade functions are missing. No changes made.')
js=re.sub(r'function dphZip\(a\)\{.*?(?=function dphWend\(a\)\{)',lambda _:new_zip,js,count=1,flags=re.S)

css_fix='''
/* DPH ZIP CHECKPOINTS V2: don't stretch the opposite card when revealing a solution */
.game-grid {align-items:start!important;grid-auto-rows:max-content!important}
.game-grid > .game-card {align-self:start!important;height:auto!important}
.game-card > .card-desc {flex-grow:0!important}
/* Numbers are original checkpoints. Keep route line below them. */
.zip-path-wrap .board-cell span {font-size:12px;min-width:20px;min-height:20px;font-weight:850}
'''
if '/* DPH ZIP CHECKPOINTS V2' not in css:css+='\n'+css_fix

# Cache-bust assets: a version parameter on the page URL doesn't invalidate CSS/JS caches.
html=re.sub(r'(href="style\.css)(?:\?[^" ]*)?(" )', r'\1?v=zip-checkpoints-v2\2', html)
html=re.sub(r'(href="style\.css)(?:\?[^" ]*)?("\s*/?>)', r'\1?v=zip-checkpoints-v2\2', html)
html=re.sub(r'(src="app\.js)(?:\?[^" ]*)?("\s+defer)', r'\1?v=zip-checkpoints-v2\2', html)

# Verified checkpoint locations for these two archive days. For future dates,
# extract structured "1 → 2: R4C2 → ... → R7C2" checkpoint segments when available.
# Never infer checkpoints from arbitrary cell-count indexes.
extractor='''\n# DPH ZIP CHECKPOINTS V2: verified number -> row/column positions
ZIP_KNOWN_CHECKPOINTS={
 '2026-11-01':[(1,4,2),(2,7,2),(3,4,5),(4,2,2),(5,2,3),(6,3,5),(7,4,1),(8,8,2),(9,6,4),(10,5,8),(11,1,7),(12,2,7),(13,5,7),(14,7,7),(15,7,6),(16,5,4)],
 '2026-11-02':[(1,1,1),(2,1,4),(3,2,5),(4,3,5),(5,3,3),(6,1,3),(7,1,2),(8,4,2),(9,5,3),(10,4,5),(11,5,4)],
}

def zip_checkpoints(text, path, day):
    """Extract true numbered checkpoints. Verify against solution-path ordering."""
    known=ZIP_KNOWN_CHECKPOINTS.get(day)
    if known:
        candidates=known
    else:
        locations={}
        pairs=list(re.finditer(r'\\b(\\d{1,2})\\s*(?:→|->)\\s*(\\d{1,2})\\s*:',text))
        for i,m in enumerate(pairs):
            sec=text[m.end():(pairs[i+1].start() if i+1<len(pairs) else len(text))]
            coords=[tuple(map(int,x)) for x in re.findall(r'R(\\d+)C(\\d+)',sec)[:150]]
            if not coords:continue
            n1,n2=map(int,m.groups())
            if n2!=n1+1:continue
            if n1 in locations and locations[n1]!=coords[0]:return None
            if n2 in locations and locations[n2]!=coords[-1]:return None
            locations[n1]=coords[0];locations[n2]=coords[-1]
        candidates=[(n,*pos) for n,pos in sorted(locations.items())]
    if len(candidates)<2 or [a for a,*_ in candidates]!=list(range(1,len(candidates)+1)):return None
    step_lookup={tuple(rc):i for i,rc in enumerate(path)}
    steps=[step_lookup.get((r,c)) for _,r,c in candidates]
    if any(step is None for step in steps) or steps[0]!=0 or steps[-1]!=len(path)-1 or steps!=sorted(set(steps)):return None
    return [list(row) for row in candidates]
\n'''
if 'ZIP_KNOWN_CHECKPOINTS' not in py:
    anchor='def update_linkedin(day,out):'
    if anchor not in py:raise SystemExit('Cannot locate LinkedIn updater. No changes made.')
    py=py.replace(anchor,extractor+anchor,1)

if "if game=='zip':\n                result['checkpoints']" not in py:
    anchor='        if result:\n'
    # Must change only the LinkedIn update function, never the other importers.
    fn_start=py.index('def update_linkedin(day,out):'); fn_end=py.index('def update_wordle(day,out):')
    piece=py[fn_start:fn_end]
    if anchor not in piece:raise SystemExit('Unexpected LinkedIn result block. No changes made.')
    piece=piece.replace(anchor,"""        if result:
            if game=='zip':
                result['checkpoints']=zip_checkpoints(txt,result['path'],day.isoformat())
                if result['checkpoints'] is None:result.pop('checkpoints')
""",1)
    py=py[:fn_start]+piece+py[fn_end:]

ast.parse(py)

# The JSON archive must have checkpoints too; these are safe only when all
# supplied coordinates belong to the actual recorded route in strict order.
def enrich_data():
    changed=0
    for f in sorted((root/'data').glob('????-??-??.json')):
        obj=json.loads(f.read_text(encoding='utf-8'))
        game=obj.get('games',{}).get('zip')
        if not game or game.get('status')!='verified' or not game.get('answer',{}).get('path'):continue
        answer=game['answer']
        checkpoints=ZIP_KNOWN_CHECKPOINTS.get(obj.get('date'))
        if not checkpoints:continue
        lookup={tuple(pos):i for i,pos in enumerate(answer['path'])}
        steps=[lookup.get((r,c)) for _,r,c in checkpoints]
        if any(s is None for s in steps) or steps[0]!=0 or steps[-1]!=len(answer['path'])-1 or steps!=sorted(set(steps)):
            print('SKIPPED unmatching checkpoint route:', f.name)
            continue
        value=[list(x) for x in checkpoints]
        if answer.get('checkpoints')!=value:
            answer['checkpoints']=value
            f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');changed+=1
    return changed

# Write only after all checks have passed.
for p,value in ((js_file,js),(css_file,css),(html_file,html),(py_file,py)):
    if p.read_text(encoding='utf-8')!=value:
        p.write_text(value,encoding='utf-8'); print('Updated:',p.relative_to(root))
print('Updated dated answer files:',enrich_data())
print('Next run: python scripts/validate.py && python scripts/embed.py')
