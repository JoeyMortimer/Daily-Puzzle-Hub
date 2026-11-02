#!/usr/bin/env python3
"""Daily Puzzle Hub visual improvements (safe, rerunnable patch).

For use in the repository root. Does NOT claim missing daily solutions are verified.
Works with the original website plus the previous fix_puzzle_parsing.py patch.
"""
from pathlib import Path
import re, ast, json

root=Path.cwd()
js_path=root/'app.js'
css_path=root/'style.css'
up_path=root/'scripts'/'update.py'
if not all(p.is_file() for p in [js_path,css_path,up_path]):
    raise SystemExit('Run this from the repository root alongside app.js and style.css')

js=js_path.read_text(encoding='utf-8')
css=css_path.read_text(encoding='utf-8')
up=up_path.read_text(encoding='utf-8')
if '/* DPH VISUAL UPGRADE V1 */' in js:
    print('Visual upgrade already present; no changes needed.')
    raise SystemExit(0)

if 'function answerHTML(a,g)' not in js or "case 'queens':" not in js or "case 'zip':" not in js or "case 'words':" not in js:
    raise SystemExit('Unexpected app.js version; no files changed')

helpers=r'''/* DPH VISUAL UPGRADE V1 */
const DPH_BOARD_COLOURS=['#f1cfdd','#e4d7f5','#edf1a9','#f2e4cd','#ffd7af','#f6b9a7','#bedaf7','#cae8d0','#dbdfe4'];
const DPH_REGION_COLOURS={
 'rose pink':'#f1cfdd','lavender':'#e4d7f5','lime yellow':'#edf1a9',
 'warm beige':'#f2e4cd','peach orange':'#ffd7af','vibrant coral':'#f6b9a7',
 'soft blue':'#bedaf7','pastel green':'#cae8d0','light gray':'#dbdfe4'
};
function dphRegionColour(key){
 if(typeof key==='number' && Number.isInteger(key))return DPH_BOARD_COLOURS[((key%DPH_BOARD_COLOURS.length)+DPH_BOARD_COLOURS.length)%DPH_BOARD_COLOURS.length];
 if(typeof key==='string')return DPH_REGION_COLOURS[key.toLowerCase().trim()]||'#e3e9e5';
 return '#e3e9e5';
}
function dphQueens(a){
 const n=a.cols.length;
 const actual=Array.isArray(a.regions)&&a.regions.length===n&&a.regions.every(row=>Array.isArray(row)&&row.length===n);
 const crownRegions=Array.isArray(a.crownRegions)&&a.crownRegions.length===n?a.crownRegions:null;
 const cells=[];
 for(let r=0;r<n;r++)for(let c=0;c<n;c++){
   const queen=a.cols[r]===c+1;
   const region=actual?a.regions[r][c]:queen&&crownRegions?crownRegions[r]:null;
   const bg=region!==null&&region!==undefined?dphRegionColour(region):'#eef3ed';
   cells.push(`<div class="board-cell ${queen?'queen':''}" style="background:${bg}!important" title="Row ${r+1}, column ${c+1}${queen?', queen':''}" aria-label="Row ${r+1}, column ${c+1}${queen?', queen':''}">${queen?'♛':''}</div>`);
 }
 const note=actual?'Colours show the original puzzle regions.':crownRegions?'Queen squares are coloured by their published region names. Other region boundaries are not yet available.':'Queen positions shown. Original colour-region map is not available yet.';
 return `<div class="game-board queens-board" style="grid-template-columns:repeat(${n},minmax(0,1fr))">${cells.join('')}</div><p class="answer-desc">${note} Queen columns by row: ${esc(a.cols.join(', '))}.</p>`;
}
function dphZip(a){
 const path=a.path||[];const side=Math.sqrt(path.length);
 if(!Number.isInteger(side)||side<3)return '<p class="answer-desc">Route data is incomplete.</p>';
 const index=Array.from({length:side},()=>Array(side).fill(null));
 path.forEach(([r,c],i)=>{if(index[r-1]&&c>0&&c<=side)index[r-1][c-1]=i+1});
 const cells=index.flat().map(v=>`<div class="board-cell ${v===1?'start':v===path.length?'end':''}" aria-label="Step ${esc(v||'?')}"><span>${v===1?'1':v===path.length?esc(v):v%5===0?esc(v):'·'}</span></div>`).join('');
 const points=path.map(([r,c])=>`${(c-.5)*100},${(r-.5)*100}`).join(' ');
 const [r0,c0]=path[0], [r1,c1]=path[path.length-1];
 return `<div class="zip-path-wrap" role="img" aria-label="Connected route through ${path.length} tiles, starting at row ${r0} column ${c0} and ending at row ${r1} column ${c1}"><div class="game-board zip-board zip-line-board" style="grid-template-columns:repeat(${side},minmax(0,1fr))">${cells}</div><svg class="zip-route" viewBox="0 0 ${side*100} ${side*100}" preserveAspectRatio="none" aria-hidden="true"><polyline points="${points}" fill="none" stroke="#087c68" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/><circle cx="${(c0-.5)*100}" cy="${(r0-.5)*100}" r="22" fill="#27855c"/><circle cx="${(c1-.5)*100}" cy="${(r1-.5)*100}" r="22" fill="#3071b5"/></svg></div><p class="answer-desc">The green line is the actual route through all ${path.length} cells. The start and finish are marked; every fifth step is numbered.</p>`;
}
function dphWend(a){
 const words=Array.isArray(a.words)?a.words:[];
 const colours=['#d8e8ff','#f6d6e6','#fce6b4','#d6efd3','#e2d8fb','#f7d8ca','#e2ead6','#dce5f0'];
 const grid=a.grid;
 const paths=a.paths;
 const validShape=Array.isArray(grid)&&grid.length>0&&grid.every(row=>Array.isArray(row)&&row.length===grid[0].length)&&Array.isArray(paths)&&paths.length===words.length&&paths.every((p,i)=>Array.isArray(p)&&p.length===words[i].length);
 const actual=validShape&&(()=>{
   const used=new Set();let count=0;
   for(const row of grid)for(const cell of row)if(cell!==null&&cell!==''&&cell!=='#')count++;
   for(let i=0;i<paths.length;i++){
     let spelling='';let previous=null;
     for(const pos of paths[i]){
       if(!Array.isArray(pos)||pos.length!==2)return false;
       const [r,c]=pos, key=`${r},${c}`;
       if(!Number.isInteger(r)||!Number.isInteger(c)||r<1||r>grid.length||c<1||c>grid[0].length||used.has(key))return false;
       if(previous&&Math.abs(previous[0]-r)+Math.abs(previous[1]-c)!==1)return false;
       const cell=grid[r-1][c-1];if(!cell||cell==='#')return false;
       used.add(key);spelling+=cell;previous=pos;
     }
     if(spelling.toUpperCase()!==words[i].toUpperCase())return false;
   }
   return used.size===count;
 })();
 if(actual){
   const n=grid[0].length;const positionMap=new Map();
   paths.forEach((path,wi)=>path.forEach((pos,k)=>{if(Array.isArray(pos)&&pos.length===2)positionMap.set(`${pos[0]},${pos[1]}`,wi)}));
   const cells=grid.map((row,r)=>row.map((letter,c)=>{
     const blocked=letter===null||letter==='#'||letter==='';
     const wi=positionMap.get(`${r+1},${c+1}`);
     const bg=blocked?'#394d50':wi===undefined?'#edf3ee':colours[wi%colours.length];
     return `<div class="board-cell ${blocked?'wend-wall':''}" style="background:${bg}!important" aria-label="${blocked?'Blocked cell':`Row ${r+1} column ${c+1}: ${esc(letter)}`}">${blocked?'':esc(letter)}</div>`;
   }).join('')).join('');
   return `<div class="game-board wend-board" style="grid-template-columns:repeat(${n},minmax(0,1fr))">${cells}</div><p class="answer-desc">The letter colours show each word's route in the original puzzle board.</p><div class="answer-tag-row">${words.map((w,i)=>`<span class="answer-tag" style="background:${colours[i%colours.length]}">${esc(w)}</span>`).join('')}</div>`;
 }
 // Exact original row/column positions are not provided by the current importer.
 // Avoid inventing a board or falsely presenting a made-up path as official.
 const rows=words.map((w,i)=>`<div class="wend-word-row" aria-label="${esc(w)}"><span class="wend-word-name">${esc(w)}</span><div class="wend-word-tiles">${[...w].map(ch=>`<span style="background:${colours[i%colours.length]}">${esc(ch)}</span>`).join('')}</div></div>`).join('');
 return `<div class="wend-word-rows">${rows}</div><p class="answer-desc">These are the solved words shown as letter tiles, not their original board positions. The full board and connected word paths need additional source data.</p>`;
}
'''
js=js.replace('function answerHTML(a,g){',helpers+'\nfunction answerHTML(a,g){',1)

# Modify answer-specific cases while preserving all other games.
def replace_case(src,case_name,new_section,next_case):
    a=src.find("  case '"+case_name+"':")
    b=src.find("  case '"+next_case+"':",a)
    if a<0 or b<a:raise RuntimeError(f'Could not locate {case_name} case')
    return src[:a]+new_section+'\n'+src[b:]

js=replace_case(js,'words',"  case 'words':return g.id==='wend'?dphWend(a):`<div class=\"answer-tag-row\">${a.words.map(w=>`<span class=\"answer-tag\">${esc(w)}</span>`).join('')}</div>`;",'ladder')
js=replace_case(js,'queens',"  case 'queens':return dphQueens(a);",'sudoku')
js=replace_case(js,'zip',"  case 'zip':return dphZip(a);",'patches')
# Mathler can have varying targets. Never hardcode '= 2' into all days.
js=js.replace('`<div class="math-answer">${esc(a.value)} = 2</div><p class="answer-desc">${esc(a.description||\'\')}</p>`', '`<div class="math-answer">${esc(a.value)}${a.target!==undefined?` = ${esc(a.target)}`:\'\'}</div><p class="answer-desc">${esc(a.description||\'\')}</p>`')
# Correct the confusing Crosswordle identity from original reverse Wordle to the swap-grid edition.
js=js.replace("desc:'Reverse-Wordle: build guesses to fit coloured clues.',play:'https://crosswordle.vercel.app/'","desc:'Swap letter tiles to complete the daily crossword grid.',play:'https://crosswordle.com/'")
old_other="const other=g.id==='crosswordle'?`<a href=\"https://crosswordle.com/\" target=\"_blank\" rel=\"noopener noreferrer\">Swap-based variant ↗</a>`:'';"
new_other="const other=g.id==='crosswordle'?`<a href=\"https://www.wordunscrambler.net/crosswordle-solver/\" target=\"_blank\" rel=\"noopener noreferrer\">Open daily grid solver ↗</a>`:g.id==='mathler'?`<a href=\"https://www.fiveletterwords.io/mathler-solver\" target=\"_blank\" rel=\"noopener noreferrer\">Open Mathler helper ↗</a>`:'';"
if old_other not in js:raise SystemExit('Unexpected card link, no files changed')
js=js.replace(old_other,new_other,1)

css_append='''
/* DPH VISUAL UPGRADE V1: solved-board layouts */
.queens-board .board-cell{font-size:clamp(16px,3vw,25px);border:1px solid #7b989266;border-radius:2px;aspect-ratio:1}
.queens-board .board-cell.queen{color:#173e39!important;text-shadow:0 1px 0 #fff9}
.zip-path-wrap{max-width:330px;width:100%;margin:10px auto;position:relative}
.zip-path-wrap .game-board{max-width:none;margin:0;gap:0;position:relative;z-index:4}
.zip-path-wrap .board-cell{background:transparent!important;border:1px solid #9fbcb2aa;border-radius:0;position:relative;color:#18513b;font-size:10px}
.zip-path-wrap .board-cell span{position:relative;z-index:6;display:grid;place-items:center;min-width:15px;min-height:15px;border-radius:50%;background:#f9fffae6;padding:1px}
.zip-path-wrap .board-cell.start span{background:#bcefc4;color:#0d5c36}
.zip-path-wrap .board-cell.end span{background:#c3def8;color:#134a7b}
.zip-path-wrap svg.zip-route{position:absolute;inset:0;width:100%;height:100%;z-index:3;pointer-events:none;overflow:visible}
.wend-word-rows{display:flex;flex-direction:column;gap:12px;margin:12px 0}
.wend-word-row{display:flex;flex-wrap:wrap;align-items:center;gap:7px}
.wend-word-name{font-size:10px;font-weight:800;color:var(--muted);min-width:70px}
.wend-word-tiles{display:flex;gap:3px;flex-wrap:wrap}
.wend-word-tiles span{width:31px;height:32px;border:1px solid #5a706c66;border-radius:5px;display:grid;place-items:center;font-size:15px;font-weight:850;color:#153e36}
.wend-board .board-cell{border:1px solid #97b9aa88;border-radius:4px;font-size:clamp(14px,3vw,22px);font-weight:850}
.wend-board .wend-wall{box-shadow:inset 0 0 0 1px #324449}
body.dark .wend-word-tiles span, body.dark .queens-board .queen {color:#163630!important}
'''
if '/* DPH VISUAL UPGRADE V1: solved-board layouts */' not in css:css+='\n'+css_append

# Add authentic crown region NAMES (not invented region geometries) for a single
# independently corroborated published puzzle. Future days can carry a.regions.
marker="        if result:\n            out['games'][game]={'status':'verified'"
if marker in up:
    up=up.replace(marker,"""        if result:
            if game=='queens' and day.isoformat()=='2026-11-02':
                # Row-by-row region names reported by two independent puzzle guides.
                # Full original board region geometry is NOT available from this feed.
                result['crownRegions']=['Lavender','Pastel Green','Light Gray','Vibrant Coral','Lime Yellow','Soft Blue','Peach Orange']
            out['games'][game]={'status':'verified'""",1)
else:raise SystemExit('Unexpected LinkedIn update parser. No files changed')
# This site was initially using the reverse-Wordle "Crosswordle", not
# the user's intended daily tile-swapping game at crosswordle.com.
old_crosswordle="obj['games']['crosswordle']={'status':'guide','number':'Original game','hint':['The original has no unique single solution.'],'answer':{'type':'notice','title':'No single fixed answer','value':'Fill real guesses that match the coloured reverse-Wordle pattern. Multiple solutions can be valid.'},'source':'https://allthedles.com/games/crosswordle/'}"
new_crosswordle="obj['games']['crosswordle']={'status':'guide','number':'Daily 7×7 / 9×9','hint':['Swap the scrambled letters into solved words.'],'answer':{'type':'notice','title':'Daily grid not yet verified','value':'This is the tile-swapping Crosswordle at crosswordle.com. A validated completed board has not yet been imported. The daily solver link below may help.'},'source':'https://crosswordle.com/'}"
if old_crosswordle in up:
    up=up.replace(old_crosswordle,new_crosswordle,1)
elif new_crosswordle not in up:
    raise SystemExit('Unexpected Crosswordle guide entry. No files changed')
ast.parse(up)

for p,s in [(js_path,js),(css_path,css),(up_path,up)]:
    p.write_text(s,encoding='utf-8')
    print('Updated:',p.relative_to(root))

# Fix previously stored Crosswordle guide text on all dated pages, and
# enrich a known-day Queens answer with independently published crown regions.
for p in sorted((root/'data').glob('????-??-??.json')):
    ob=json.loads(p.read_text(encoding='utf-8'))
    cb=ob.get('games',{}).get('crosswordle')
    dirty=False
    if cb and cb.get('status')=='guide':
        cb.update({'number':'Daily 7×7 / 9×9','hint':['Swap scrambled letters into solved words.'],
                   'answer':{'type':'notice','title':'Daily grid not yet verified',
                   'value':'This is the tile-swapping Crosswordle at crosswordle.com. A validated completed board has not yet been imported. The daily solver link below may help.'},
                   'source':'https://crosswordle.com/'})
        dirty=True
    queen=ob.get('games',{}).get('queens',{})
    if p.stem=='2026-11-02' and queen.get('status')=='verified' and queen.get('number')=='#916' and queen.get('answer',{}).get('cols')==[7,2,4,6,3,5,1]:
        queen['answer']['crownRegions']=['Lavender','Pastel Green','Light Gray','Vibrant Coral','Lime Yellow','Soft Blue','Peach Orange']
        dirty=True
    if dirty:
        p.write_text(json.dumps(ob,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Enhanced:',p.relative_to(root))

print('Next: python scripts/validate.py && python scripts/embed.py')
