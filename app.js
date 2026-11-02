'use strict';
const GAMES = [
 {id:'wordle',title:'Wordle',category:'nyt',kind:'WORD GAME',icon:'W',colour:'green',desc:'The world’s favourite five-letter daily guessing game.',play:'https://www.nytimes.com/games/wordle/index.html'},
 {id:'strands',title:'Strands',category:'nyt',kind:'WORD SEARCH',icon:'S',colour:'blue',desc:'Find all the themed words and the hidden spangram.',play:'https://www.nytimes.com/games/strands'},
 /* DPH-CROSSWORDLE-HONEST-STATUS-V2 */
 {id:'crosswordle',title:'Crosswordle',category:'nyt',kind:'WORD LOGIC',icon:'C',colour:'purple',desc:'Swap letter tiles to complete the daily crossword grid.',play:'https://crosswordle.com/'},
 {id:'mathler',title:'Mathler',category:'math',kind:'NUMBER PUZZLE',icon:'÷',colour:'gold',desc:'Find the six-character hidden calculation.',play:'https://www.mathler.com/'},
 {id:'sumplete',title:'Sumplete',category:'math',kind:'NUMBER LOGIC',icon:'∑',colour:'coral',desc:'Keep or remove numbers to hit each row and column total.',play:'https://sumplete.com/'},
 {id:'pinpoint',title:'Pinpoint',category:'linkedin',kind:'LINKEDIN · WORDS',icon:'◎',colour:'green',desc:'Find the category shared by five clues.',play:'https://www.linkedin.com/games/pinpoint'},
 {id:'crossclimb',title:'Crossclimb',category:'linkedin',kind:'LINKEDIN · WORDS',icon:'↟',colour:'purple',desc:'Solve trivia clues and arrange a one-letter word ladder.',play:'https://www.linkedin.com/games/crossclimb'},
 {id:'queens',title:'Queens',category:'linkedin',kind:'LINKEDIN · LOGIC',icon:'♛',colour:'gold',desc:'Place one queen in every row, column and colour region.',play:'https://www.linkedin.com/games/queens'},
 {id:'tango',title:'Tango',category:'linkedin',kind:'LINKEDIN · LOGIC',icon:'☯',colour:'blue',desc:'Balance suns and moons on a logic grid.',play:'https://www.linkedin.com/games/tango'},
 {id:'zip',title:'Zip',category:'linkedin',kind:'LINKEDIN · LOGIC',icon:'↝',colour:'coral',desc:'Draw a route through every cell in the right order.',play:'https://www.linkedin.com/games/zip'},
 {id:'mini-sudoku',title:'Mini Sudoku',category:'linkedin',kind:'LINKEDIN · NUMBERS',icon:'▦',colour:'green',desc:'A quick six-by-six Sudoku with smaller boxes.',play:'https://www.linkedin.com/games/mini-sudoku'},
 {id:'patches',title:'Patches',category:'linkedin',kind:'LINKEDIN · LOGIC',icon:'▥',colour:'purple',desc:'Fit rectangular patches over the entire board.',play:'https://www.linkedin.com/games/patches'},
 {id:'wend',title:'Wend',category:'linkedin',kind:'LINKEDIN · WORDS',icon:'≈',colour:'blue',desc:'Trace winding word paths that use every letter.',play:'https://www.linkedin.com/games/wend'}
];
const $=id=>document.getElementById(id);
const storage={get:(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}},set:(key,value)=>{try{localStorage.setItem(key,JSON.stringify(value))}catch{}}};
let dayData=null,selectedDay='',activeFilter='all',searchText='',favourites=storage.get('dph:favourites',[]),revealed=new Set();
const embedded=(()=>{try{return JSON.parse($('embedded-data').textContent)}catch{return null}})();
const esc=(str)=>String(str??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
function ukToday(){const parts=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const p=Object.fromEntries(parts.map(x=>[x.type,x.value]));return `${p.year}-${p.month}-${p.day}`}
function prettyDate(day){return new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(day+'T12:00:00Z'))}
function addDays(day,delta){const d=new Date(day+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+delta);return d.toISOString().slice(0,10)}
function safeExternal(url){try{const u=new URL(url);return /^https?:$/.test(u.protocol)?u.href:'#'}catch{return '#'}}
async function selectDate(day){if(!/^\d{4}-\d{2}-\d{2}$/.test(day))return;selectedDay=day;revealed.clear();$('date-input').value=day;$('date-heading').textContent=prettyDate(day);const notice=$('data-notice');notice.hidden=true;const snapshot=day;
  /* Prefer the latest daily JSON over embedded data. */
  try{const response=await fetch(`data/${day}.json`,{cache:'no-store'});if(!response.ok)throw new Error('No daily data');const found=await response.json();if(found.date!==day)throw new Error('Wrong date');if(selectedDay!==snapshot)return;dayData=found}
  catch(_){if(selectedDay!==snapshot)return;if(embedded&&embedded.date===day){dayData=embedded;render();return;}dayData={date:day,games:{}};notice.textContent=`We don't have checked answers for ${prettyDate(day)} yet. You can still open each game or its answer-source link. We never display an older puzzle as today's answer.`;notice.hidden=false}
  render();
}
function gameStatus(d){if(!d)return {label:'NOT YET VERIFIED',cls:'missing'};if(d.status==='verified')return {label:'✓ ANSWER VERIFIED',cls:''};if(d.status==='missing')return {label:'NOT YET VERIFIED',cls:'missing'};if(d.status==='example')return {label:'EXAMPLE ONLY',cls:'example'};return {label:'GUIDE AVAILABLE',cls:'guide'}}
function cardHTML(g){const d=dayData?.games?.[g.id];const status=gameStatus(d);const saved=favourites.includes(g.id),isRevealed=revealed.has(g.id);const number=d?.number?esc(d.number):'Awaiting answer';let answer='';if(isRevealed)answer=`<div class="answer-area"><div class="answer-label">${d?.status==='verified'?'THE ANSWER':'WHAT WE KNOW'}</div>${answerHTML(d?.answer,g)}${d?.status==='example'?'<p class="answer-desc">Example, not an independently verified daily solution.</p>':''}</div>`;
 const source=d?.source?`<a href="${esc(safeExternal(d.source))}" target="_blank" rel="noopener noreferrer">View source ↗</a>`:'<span style="font-size:10px;color:#97a69e">No checked source for this date</span>';
 const hints=d?.hint?.length?`<details class="hint-details"><summary>Need a hint instead?</summary><ol class="hint-list">${d.hint.map(h=>`<li>${esc(h)}</li>`).join('')}</ol></details>`:'';
 const other=g.id==='crosswordle'?`<a href="https://www.wordunscrambler.net/crosswordle-solver/" target="_blank" rel="noopener noreferrer">Open daily grid solver ↗</a>`:g.id==='mathler'?`<a href="https://www.fiveletterwords.io/mathler-solver" target="_blank" rel="noopener noreferrer">Open Mathler helper ↗</a>`:g.id==='wend'?`<a href="https://www.thewordfinder.com/linkedin-games-hub/wend-hints/" target="_blank" rel="noopener noreferrer">Open full Wend grid ↗</a>`:'';
 return `<article class="game-card" data-game="${esc(g.id)}"><div class="card-top"><div class="game-identity"><div class="game-icon ${g.colour}" aria-hidden="true">${esc(g.icon)}</div><div><h3 class="game-title">${esc(g.title)}</h3><div class="game-type">${esc(g.kind)}</div></div></div><button class="save-btn ${saved?'is-saved':''}" type="button" data-save="${g.id}" aria-label="${saved?'Remove':'Add'} ${g.title} ${saved?'from':'to'} favourites" aria-pressed="${saved}">${saved?'★':'☆'}</button></div><p class="card-desc">${esc(g.desc)}</p><div class="card-meta"><span class="card-number">${number}</span><span class="card-status ${status.cls}">${status.label}</span></div><div class="card-actions"><button class="reveal-button" type="button" data-reveal="${g.id}" aria-expanded="${isRevealed}" ${!d||d.status==='missing'?'disabled title="No checked answer for this date"':''}>${isRevealed?'Hide answer ↑':d?.status==='verified'?'Reveal answer ↓':d?.status==='missing'||!d?'Awaiting answer':'View guide ↓'}</button><a class="play-button" href="${esc(safeExternal(g.play))}" target="_blank" rel="noopener noreferrer" aria-label="Play ${esc(g.title)} on the original website">Play ↗</a></div>${hints}${answer}<div class="source-row">${source}${other}</div></article>`;
}
function gridHTML(rows,cls,extraClass=(r,c,v)=>'',renderCell=(r,c,v)=>esc(v)){const cols=rows[0]?.length||0;return `<div class="game-board ${cls}" style="grid-template-columns:repeat(${cols},minmax(0,1fr))">${rows.map((row,r)=>row.map((v,c)=>`<div class="board-cell ${extraClass(r,c,v)}" aria-label="Row ${r+1}, column ${c+1}: ${esc(v)}">${renderCell(r,c,v)}</div>`).join('')).join('')}</div>`}
/* DPH VISUAL UPGRADE V1 */
/* DPH-QUEENS-REGION-BORDERS-V2 */
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
    // Region outlines are only drawn when the entire original map is known.
    const borders=actual?[
      r===0||a.regions[r-1][c]!==region?'border-top:3px solid #34544a':'',
      c===0||a.regions[r][c-1]!==region?'border-left:3px solid #34544a':'',
      r===n-1||a.regions[r+1][c]!==region?'border-bottom:3px solid #34544a':'',
      c===n-1||a.regions[r][c+1]!==region?'border-right:3px solid #34544a':''
    ].filter(Boolean).join(';'):'';
   cells.push(`<div class="board-cell ${queen?'queen':''}" style="background:${bg}!important;${borders}" title="Row ${r+1}, column ${c+1}${queen?', queen':''}" aria-label="Row ${r+1}, column ${c+1}${queen?', queen':''}">${queen?'♛':''}</div>`);
 }
 const note=actual?'Colours show the original puzzle regions.':crownRegions?'Queen squares are coloured by their published region names. Other region boundaries are not yet available.':'Queen positions shown. Original colour-region map is not available yet.';
 return `<div class="game-board queens-board" style="grid-template-columns:repeat(${n},minmax(0,1fr))">${cells.join('')}</div><p class="answer-desc">${note} Queen columns by row: ${esc(a.cols.join(', '))}.</p>`;
}
function dphZip(a){
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
/* DPH-WEND-BOARD-ENHANCEMENT-V2 */
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
     return `<div class="board-cell ${blocked?'wend-wall':''}" style="background:${bg}!important" title="R${r+1}C${c+1}${blocked?' blocked':` · ${esc(letter)}`}" aria-label="${blocked?'Blocked cell':`Row ${r+1} column ${c+1}: ${esc(letter)}`}">${blocked?'':esc(letter)}</div>`;
   }).join('')).join('');
   return `<div class="game-board wend-board" style="grid-template-columns:repeat(${n},minmax(0,1fr))">${cells}</div><p class="answer-desc">The letter colours show each word's route in the original puzzle board.</p><div class="answer-tag-row">${words.map((w,i)=>`<span class="answer-tag" style="background:${colours[i%colours.length]}">${esc(w)}</span>`).join('')}</div>`;
 }
 // Exact original row/column positions are not provided by the current importer.
 // Avoid inventing a board or falsely presenting a made-up path as official.
 const rows=words.map((w,i)=>`<div class="wend-word-row" aria-label="${esc(w)}"><span class="wend-word-name">${esc(w)}</span><div class="wend-word-tiles">${[...w].map(ch=>`<span style="background:${colours[i%colours.length]}">${esc(ch)}</span>`).join('')}</div></div>`).join('');
 return `<div class="wend-word-rows">${rows}</div><p class="answer-desc">These are the solved words shown as letter tiles, not their original board positions. The full board and connected word paths need additional source data.</p>`;
}

/* CROSSWORDLE-BOARD-V1 */
function dphCrosswordle(a){const rows=a.rows;
 if(!Array.isArray(rows)||![7,9].includes(rows.length)||!rows.every(row=>Array.isArray(row)&&row.length===rows.length&&row.every(ch=>typeof ch==='string'&&(ch==='#'||/^[A-Z]$/i.test(ch)))))return '<p class="answer-desc">No verified completed Crosswordle board available.</p>';
 return gridHTML(rows,'crosswordle-board',(_r,_c,v)=>v==='#'?'wall':'',(_r,_c,v)=>v==='#'?'':esc(v.toUpperCase()));}

function dphWordle(a){
  const word = String(a?.value || a?.word || '').toUpperCase().trim();
  if(!/^[A-Z]{5}$/.test(word)) return null;

  const rows = [];
  for(let r=0;r<6;r++){
    for(let c=0;c<5;c++){
      const filled = r===2;
      rows.push(
        `<div class="board-cell ${filled?'filled correct':'empty'}">${
          filled ? esc(word[c]) : ''
        }</div>`
      );
    }
  }

  return `<div class="wordle-wrap">
    <div class="game-board wordle-board"
      style="grid-template-columns:repeat(5,minmax(0,1fr))">
      ${rows.join('')}
    </div>
    <p class="answer-desc">Answer shown in a Wordle-style grid.</p>
  </div>`;
}

function dphMathler(a){
  const expr = String(a?.value || a?.equation || '').replace(/\s+/g,'');
  if(!expr || expr.length < 3) return null;

  const chars = expr.split('');
  const cols = chars.length;
  const cells = [];

  for(let r=0;r<6;r++){
    for(let c=0;c<cols;c++){
      const filled = r===3;
      cells.push(
        `<div class="board-cell ${filled?'filled correct':'empty'}">${
          filled ? esc(chars[c]) : ''
        }</div>`
      );
    }
  }

  return `<div class="mathler-wrap">
    <div class="mathler-title">MATHLER</div>
    <div class="game-board mathler-board"
      style="grid-template-columns:repeat(${cols},minmax(0,1fr))">
      ${cells.join('')}
    </div>
    <p class="answer-desc">Verified daily equation shown in a Mathler-style grid.</p>
  </div>`;
}

function dphPatches(a){
  const rects = Array.isArray(a?.rects) ? a.rects : [];
  if(!rects.length) return null;

  const side = Math.max(...rects.flat());
  const colours = [
    '#a78bfa','#6ee7b7','#7dd3fc','#f87171','#fdba74',
    '#f472b6','#c4b5fd','#fcd34d','#86efac','#93c5fd'
  ];

  const bgCells = [];
  for(let r=1;r<=side;r++){
    for(let c=1;c<=side;c++){
      bgCells.push(`<div class="patch-bg-cell"></div>`);
    }
  }

  const blocks = rects.map((rect,i)=>{
    const [r1,c1,r2,c2] = rect;
    const area = (r2-r1+1)*(c2-c1+1);
    const height = r2-r1+1;
    const width = c2-c1+1;
    return `<div class="patch-shape"
      style="
        grid-row:${r1} / ${r2+1};
        grid-column:${c1} / ${c2+1};
        --patch-col:${colours[i%colours.length]};
      ">
      <span>${area}</span>
    </div>`;
  }).join('');

  return `<div class="patches-wrap">
    <div class="patches-canvas"
      style="grid-template-columns:repeat(${side},1fr);grid-template-rows:repeat(${side},1fr)">
      ${bgCells.join('')}
      ${blocks}
    </div>
    <p class="answer-desc">Solved rectangles shown as coloured patches. Numbers indicate patch size.</p>
  </div>`;
}

function answerHTML(a,g){
  const special = g?.id==='wordle' ? dphWordle(a) : g?.id==='mathler' ? dphMathler(a) : g?.id==='patches' ? dphPatches(a) : null;
  if(special) return special;if(!a)return `<p class="answer-desc">Not verified for this date. Choose “Play” to open the game.</p>`;
 switch(a.type){
  case 'word':return `<div class="answer-word">${esc(a.value)}</div>`;
  case 'strands':return `<div class="answer-desc">THEME · ${esc(a.theme)}</div><p class="answer-desc">SPANGRAM</p><div class="answer-word">${esc(a.spangram)}</div><p class="answer-desc">THEME WORDS</p><div class="answer-tag-row">${a.words.map(w=>`<span class="answer-tag">${esc(w)}</span>`).join('')}</div>`;
  case 'words':return g.id==='wend'?dphWend(a):`<div class="answer-tag-row">${a.words.map(w=>`<span class="answer-tag">${esc(w)}</span>`).join('')}</div>`;
  case 'ladder':return `<div class="answer-ladder">${a.words.map(w=>`<span>${esc(w)}</span>`).join('')}</div><p class="answer-desc">${esc(a.description||'')}</p>`;
  case 'queens':return dphQueens(a);
  case 'crosswordle':return dphCrosswordle(a);
  case 'sudoku':return gridHTML(a.rows,'sudoku-board');
  case 'tango':return gridHTML(a.rows,'tango-board',(_r,_c,v)=>v==='M'?'moon':'',(_r,_c,v)=>v==='M'?'☾':'☀');
  case 'zip':return dphZip(a);
  case 'patches':{const side=Math.max(...a.rects.map(rect=>Math.max(rect[2],rect[3])));const matrix=Array.from({length:side},()=>Array(side).fill(null));a.rects.forEach(([r1,c1,r2,c2],index)=>{for(let r=r1;r<=r2;r++)for(let c=c1;c<=c2;c++)matrix[r-1][c-1]={index,label:r===r1&&c===c1?(r2-r1+1)*(c2-c1+1):''}});const colours=['#dceaf8','#e8d9ed','#c8e6e3','#fce9bd','#f2c6be','#e8e7bd','#d5edc6','#fae1b3','#d6def5','#fbd9e9','#c4e7ef','#d7eaca','#ecddc5','#e0e2ed'];return gridHTML(matrix,'patches-board',()=>'',(_r,_c,v)=>`<span style="background:${colours[v?.index%colours.length]};width:100%;height:100%;border-radius:3px;display:grid;place-items:center">${v?.label||''}</span>`)+'<p class="answer-desc">Each colour is a rectangle. Numbers indicate patch area in cells.</p>'}
  case 'sumplete':{let out='<div class="sumplete-table">';for(let r=0;r<5;r++){for(let c=0;c<5;c++)out+=`<div class="board-cell ${a.kept[r][c]?'keep':'delete'}">${esc(a.grid[r][c])}</div>`;out+=`<div class="board-cell target">${esc(a.rowTargets[r])}</div>`}for(let c=0;c<5;c++)out+=`<div class="board-cell target">${esc(a.colTargets[c])}</div>`;out+='<div class="board-cell target">✓</div></div><p class="answer-desc">Green = keep · Red crossed out = delete · Targets shown on the right and bottom.</p>';return out}
  case 'math':return `<div class="math-answer">${esc(a.value)}${a.target!==undefined?` = ${esc(a.target)}`:''}</div><p class="answer-desc">${esc(a.description||'')}</p>`;
  case 'notice':return `<strong class="answer-word" style="font-size:17px">${esc(a.title)}</strong><p class="answer-desc">${esc(a.value)}</p>`;
  default:return '<p class="answer-desc">No compatible answer format.</p>';
 }
}


function markWendDirections(){
 const a = dayData?.games?.wend?.answer;
 const board = document.querySelector('[data-game="wend"] .wend-board');
 if(!board || !Array.isArray(a?.paths) || !Array.isArray(a?.grid)) return;

 const rows = a.grid.length, cols = a.grid[0]?.length;
 if(!cols || board.children.length !== rows*cols) return;

 const colours = ['#fa554b','#9fc000','#686cf0','#dc48a5','#e5a532','#23a99d'];
 const point = ([r,c]) => [(c-.5)*100,(r-.5)*100];
 const lines=[], arrows=[], letters=[], rings=[], ticks=[];

 a.paths.forEach((path,i)=>{
   if(!Array.isArray(path) || !path.length) return;
   const colour = colours[i%colours.length];
   const pts = path.map(p=>point(p).join(',')).join(' ');

   lines.push(
     `<polyline points="${pts}" fill="none" stroke="white"
       stroke-width="77" stroke-linecap="round"
       stroke-linejoin="round"/>
      <polyline points="${pts}" fill="none" stroke="${colour}"
       stroke-width="69" stroke-linecap="round"
       stroke-linejoin="round"/>`
   );

   path.forEach((pos,j)=>{
     const [r,c]=pos, [x,y]=point(pos), next=path[j+1];

     letters.push(
       `<text x="${x}" y="${y}" text-anchor="middle"
         dominant-baseline="central" font-size="43"
         font-weight="850" fill="#192c2c">
         ${esc(a.grid[r-1][c-1])}</text>`
     );

     if(next){
       const [nx,ny]=point(next);
       const arrow=nx>x?'›':nx<x?'‹':ny>y?'⌄':'⌃';
       arrows.push(
         `<text x="${(x+nx)/2}" y="${(y+ny)/2}"
           text-anchor="middle" dominant-baseline="central"
           font-size="37" font-weight="850"
           fill="#263b38">${arrow}</text>`
       );
     }
   });

   const [sx,sy]=point(path[0]);
   const [ex,ey]=point(path[path.length-1]);

   rings.push(
     `<circle cx="${sx}" cy="${sy}" r="32"
       fill="none" stroke="white" stroke-width="5"/>
      <circle cx="${ex}" cy="${ey}" r="31"
       fill="none" stroke="white"
       stroke-opacity=".75" stroke-width="3"/>`
   );

   ticks.push(
     `<circle cx="${sx+28}" cy="${sy-30}" r="18"
       fill="#fff" stroke="#20966b" stroke-width="3"/>
      <text x="${sx+28}" y="${sy-29}"
       text-anchor="middle" dominant-baseline="central"
       font-size="26" font-weight="850"
       fill="#20966b">✓</text>`
   );
 });

 board.insertAdjacentHTML('beforeend',
   `<svg class="wend-trail-svg"
     viewBox="0 0 ${cols*100} ${rows*100}"
     preserveAspectRatio="none" aria-hidden="true">
     ${lines.join('')}${arrows.join('')}
     ${rings.join('')}${letters.join('')}${ticks.join('')}
   </svg>`
 );

 const note=board.nextElementSibling;
 if(note?.classList.contains('answer-desc')){
   note.textContent='Follow each coloured trail from its tick to the outlined final letter. Chevrons show direction.';
 }
}

function render(){const visible=GAMES.filter(g=>(activeFilter==='all'||g.category===activeFilter||(activeFilter==='favourites'&&favourites.includes(g.id)))&&(`${g.title} ${g.desc} ${g.kind}`.toLowerCase().includes(searchText)));
 visible.sort((a,b)=>Number(favourites.includes(b.id))-Number(favourites.includes(a.id))||GAMES.indexOf(a)-GAMES.indexOf(b));$('cards').innerHTML=visible.map(cardHTML).join('');markWendDirections();$('game-count').textContent=visible.length;$('empty-search').hidden=!!visible.length;const verified=GAMES.filter(g=>dayData?.games?.[g.id]?.status==='verified').length;$('date-subtitle').textContent=`${verified} checked solutions · ${GAMES.length} games in one place.`;document.querySelectorAll('[data-filter]').forEach(el=>{const active=el.dataset.filter===activeFilter;el.classList.toggle('active',active);if(el.tagName==='BUTTON')el.setAttribute('aria-pressed',String(active))})}
function setFilter(filter){activeFilter=filter;render();if(window.innerWidth<850)$('games').scrollIntoView({behavior:'smooth',block:'start'})}
document.addEventListener('click',event=>{const filter=event.target.closest('[data-filter]');if(filter){setFilter(filter.dataset.filter);return}const btn=event.target.closest('[data-reveal]');if(btn){if(revealed.has(btn.dataset.reveal))revealed.delete(btn.dataset.reveal);else revealed.add(btn.dataset.reveal);render();return}const save=event.target.closest('[data-save]');if(save){const id=save.dataset.save;favourites=favourites.includes(id)?favourites.filter(x=>x!==id):[...favourites,id];storage.set('dph:favourites',favourites);render();return}});
$('search-input').addEventListener('input',event=>{searchText=event.target.value.trim().toLowerCase();render()});
$('date-input').addEventListener('change',event=>selectDate(event.target.value));
$('prev-day').addEventListener('click',()=>selectDate(addDays(selectedDay,-1)));
$('next-day').addEventListener('click',()=>selectDate(addDays(selectedDay,1)));
$('today-button').addEventListener('click',()=>selectDate(ukToday()));
$('theme-toggle').addEventListener('click',()=>{document.body.classList.toggle('dark');storage.set('dph:dark',document.body.classList.contains('dark'));$('theme-toggle').textContent=document.body.classList.contains('dark')?'☀':'☾'});
if(storage.get('dph:dark',false)){document.body.classList.add('dark');$('theme-toggle').textContent='☀'}
$('footer-year').textContent=String(new Date().getFullYear());
selectDate(ukToday());
