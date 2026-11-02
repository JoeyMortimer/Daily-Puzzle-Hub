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
async function selectDate(day){if(!/^\d{4}-\d{2}-\d{2}$/.test(day))return;selectedDay=day;revealed.clear();clueLevels.clear();dphProgress.clear();$('date-input').value=day;$('date-heading').textContent=prettyDate(day);const notice=$('data-notice');notice.hidden=true;const snapshot=day;
  /* Prefer the latest daily JSON over embedded data. */
  try{const response=await fetch(`data/${day}.json`,{cache:'no-store'});if(!response.ok)throw new Error('No daily data');const found=await response.json();if(found.date!==day)throw new Error('Wrong date');if(selectedDay!==snapshot)return;dayData=found}
  catch(_){if(selectedDay!==snapshot)return;if(embedded&&embedded.date===day){dayData=embedded;render();return;}dayData={date:day,games:{}};notice.textContent=`We don't have checked answers for ${prettyDate(day)} yet. You can still open each game or its answer-source link. We never display an older puzzle as today's answer.`;notice.hidden=false}
  render();
}
function gameStatus(d){if(!d)return {label:'NOT YET VERIFIED',cls:'missing'};if(d.status==='verified')return {label:'✓ ANSWER VERIFIED',cls:''};if(d.status==='missing')return {label:'NOT YET VERIFIED',cls:'missing'};if(d.status==='example')return {label:'EXAMPLE ONLY',cls:'example'};return {label:'GUIDE AVAILABLE',cls:'guide'}}
/* DPH PHASE 2: progressive clues and genuine Strands boards */
const clueLevels=new Map();

function dphClues(g,d){
  if(!d || !g)return [];
  if(Array.isArray(d.clues) && d.clues.length)return d.clues.filter(x=>typeof x==='string').slice(0,4);
  if(Array.isArray(d.hint) && d.hint.length)return d.hint.filter(x=>typeof x==='string').slice(0,4);
  const a=d.answer;
  if(d.status!=='verified' || !a)return [];
  const hints=[];
  switch(g.id){
    case 'wordle': {
      const w=String(a.value||'').toUpperCase();
      if(w.length===5)hints.push('The answer has five letters.',`It starts with ${w[0]}.`,`It ends with ${w[4]}.`);
      break;
    }
    case 'strands': {
      if(a.theme)hints.push(`The theme is “${a.theme}”.`);
      if(a.spangram)hints.push(`The spangram has ${a.spangram.length} letters.`);
      if(a.paths?.[a.spangram]?.[0]){
        const [r,c]=a.paths[a.spangram][0];
        hints.push(`The spangram starts at row ${r}, column ${c}.`);
      }else if(a.spangram)hints.push(`The spangram starts with ${a.spangram[0]}.`);
      break;
    }
    case 'queens':{
      const cols=a.cols||[];
      hints.push(`There are ${cols.length} queens: exactly one per row and column.`);
      if(cols[0])hints.push(`The queen in row 1 belongs in column ${cols[0]}.`);
      if(cols[1])hints.push(`The queen in row 2 belongs in column ${cols[1]}.`);
      break;
    }
    case 'pinpoint':{
      const phrase=String(a.value||'').trim();
      if(phrase){hints.push('Think of a shared category rather than a specific object.');hints.push(`The category begins with “${phrase[0].toUpperCase()}”.`);}
      break;
    }
    case 'crossclimb':{
      const w=a.words||[];
      if(w.length){hints.push(`The ladder has ${w.length} words of ${w[0].length} letters.`);hints.push(`The first rung is ${w[0]}.`);if(w.length>2)hints.push(`The last rung is ${w[w.length-1]}.`);}
      break;
    }
    case 'mathler':{
      const expr=String(a.value||a.equation||'');
      const ops=[...new Set((expr.match(/[+*/-]/g)||[]))];
      if(a.target!==undefined)hints.push(`Today's target is ${a.target}.`);
      if(ops.length)hints.push(`The equation uses ${ops.length} distinct operator${ops.length===1?'':'s'}.`);
      if(expr)hints.push(`The equation starts with ${expr[0]}.`);
      break;
    }
    case 'sumplete':{
      if(a.kept?.[0])hints.push(`In row 1, ${a.kept[0].filter(Boolean).length} numbers are kept.`);
      if(a.kept?.[0])hints.push(`The top-left number is ${a.kept[0][0]?'kept':'removed'}.`);
      break;
    }
    case 'zip':{
      const checkpoints=a.checkpoints||[];
      if(checkpoints.length)hints.push(`There are ${checkpoints.length} numbered checkpoints.`);
      if(checkpoints[1])hints.push(`Checkpoint 2 is in row ${checkpoints[1][1]}, column ${checkpoints[1][2]}.`);
      break;
    }
    case 'mini-sudoku':{
      if(a.rows?.[0]?.length){hints.push('Each row, column and 2×3 box contains 1–6.');hints.push(`The top-left square is ${a.rows[0][0]}.`);}
      break;
    }
    case 'tango':{
      if(a.rows?.[0]){hints.push('Each row and column has three suns and three moons.');hints.push(`Row 1, column 1 is ${a.rows[0][0]==='S'?'a sun':'a moon'}.`);}
      break;
    }
    case 'patches':{
      if(a.rects?.length){const sizes=a.rects.map(([r1,c1,r2,c2])=>(r2-r1+1)*(c2-c1+1));hints.push(`There are ${sizes.length} patches.`);hints.push(`The largest patch contains ${Math.max(...sizes)} cells.`);}
      break;
    }
    case 'wend':{
      if(a.words?.length){hints.push(`There are ${a.words.length} hidden words.`);hints.push(`The shortest word is ${Math.min(...a.words.map(w=>w.length))} letters long.`);if(a.paths?.[0]?.[0])hints.push(`One route begins at row ${a.paths[0][0][0]}, column ${a.paths[0][0][1]}.`);}
      break;
    }
    default:break;
  }
  return hints.slice(0,3);
}

function dphClueCard(g,d){
  const hints=dphClues(g,d);
  if(!hints.length)return '';
  const shown=Math.min(clueLevels.get(g.id)||0,hints.length);
  const lines=hints.slice(0,shown).map((h,i)=>`<p class="clue-line"><strong>Clue ${i+1}</strong> ${esc(h)}</p>`).join('');
  return `<section class="clue-panel" aria-label="Optional clues for ${esc(g.title)}">
     <div class="clue-panel-head"><span>NEED A CLUE?</span><small>${shown} of ${hints.length} revealed</small></div>
     ${lines}
     <div class="clue-buttons">
       ${shown<hints.length?`<button type="button" class="clue-next" data-clue="${esc(g.id)}" data-clue-action="next" aria-label="Reveal clue ${shown+1} for ${esc(g.title)}">Reveal clue ${shown+1} ↓</button>`:'<span class="clue-complete">All clues revealed</span>'}
       ${shown>0?`<button type="button" class="clue-reset" data-clue="${esc(g.id)}" data-clue-action="reset">Hide clues</button>`:''}
     </div>
     <p class="clue-disclaimer">Hints may be derived from the verified solution; they are not necessarily official puzzle clues.</p>
  </section>`;
}

function dphStrands(a){
  const theme=`<p class="answer-desc">THEME · ${esc(a.theme||'')}</p>`;
  const list=`<p class="answer-desc">SPANGRAM</p><div class="answer-word">${esc(a.spangram||'')}</div><p class="answer-desc">THEME WORDS</p><div class="answer-tag-row">${(a.words||[]).map(w=>`<span class="answer-tag">${esc(w)}</span>`).join('')}</div>`;
  const grid=a.grid;
  if(!Array.isArray(grid)||grid.length!==8||!grid.every(row=>Array.isArray(row)&&row.length===6))return theme+list+'<p class="answer-desc">Original letter board is not confirmed for this date.</p>';
  const paths=a.paths||{}, words=[...(a.words||[]),a.spangram];
  const point=([r,c])=>`${(c-.5)*100},${(r-.5)*100}`;
  const lines=[], backgrounds=new Map();
  const colours=['#b3e3f2','#a3d7ef','#bbe8ed','#a6dce8','#bddbee','#9acfe5','#bad5e9'];
  words.forEach((word,i)=>{
    const path=paths[word];
    if(!Array.isArray(path)||path.length!==word.length)return;
    const tint=i===(words.length-1)?'#ffca28':colours[i%colours.length];
    path.forEach(([r,c])=>backgrounds.set(`${r},${c}`,tint));
    lines.push(`<polyline points="${path.map(point).join(' ')}" stroke="${tint}" stroke-width="80" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`);
  });
  const cells=grid.map((row,r)=>row.map((letter,c)=>{
    const color=backgrounds.get(`${r+1},${c+1}`);
    return `<div class="strands-cell" style="${color?'background:'+color+';':''}" aria-label="Row ${r+1} column ${c+1}: ${esc(letter)}">${esc(letter)}</div>`;
  }).join('')).join('');
  return `${theme}<div class="strands-board" role="img" aria-label="Strands 6 column by 8 row letter board">${cells}${lines.length?`<svg class="strands-route-svg" viewBox="0 0 600 800" preserveAspectRatio="none" aria-hidden="true">${lines.join('')}</svg>`:''}</div>${list}<p class="answer-desc">${lines.length?'Blue trails show theme words; gold shows the spangram.':'Letter board verified; complete paths are not yet confirmed.'}</p>`;
}

function dphQueensPhase2(a){
  const n=a?.cols?.length||0;
  const regions=a.regions;
  if(!n||!Array.isArray(regions)||regions.length!==n||!regions.every(row=>Array.isArray(row)&&row.length===n))return dphQueens(a);
  const all=new Set(regions.flat().map(String));
  const queens=new Set(a.cols.map((col,r)=>String(regions[r][col-1])));
  if(all.size!==n||queens.size!==n)return dphQueens(a);
  const edge=(r,c,side)=>{
    const x=regions[r][c];
    return side==='top'?(r===0||regions[r-1][c]!==x):side==='right'?(c===n-1||regions[r][c+1]!==x):side==='bottom'?(r===n-1||regions[r+1][c]!==x):(c===0||regions[r][c-1]!==x);
  };
  const cells=regions.map((row,r)=>row.map((zone,c)=>{
    const queen=a.cols[r]===c+1;
    const style=`background:${dphRegionColour(zone)}!important;border-top:${edge(r,c,'top')?2:0.5}px solid #26302a;border-right:${edge(r,c,'right')?2:0.5}px solid #26302a;border-bottom:${edge(r,c,'bottom')?2:0.5}px solid #26302a;border-left:${edge(r,c,'left')?2:0.5}px solid #26302a;`;
    return `<div class="board-cell ${queen?'queen':''}" style="${style}" aria-label="Row ${r+1} column ${c+1}: ${queen?'queen':'empty'} in region ${esc(zone)}">${queen?'♛':'×'}</div>`;
  }).join('')).join('');
  return `<div class="game-board queens-board p2-regions" style="grid-template-columns:repeat(${n},minmax(0,1fr))">${cells}</div><p class="answer-desc">Complete verified colour-region map; one queen in every region, row and column.</p>`;
}

/* DPH REFINED CLUES AND BOARD DISPLAY V3 — actual puzzle clues, not rules. */
const dphProgress = new Map();

function dphClues(g,d){
  if(!d || d.status!=='verified' || !d.answer) return [];
  const a=d.answer, id=g?.id;
  const supplied=Array.isArray(d.clues)?d.clues.filter(x=>typeof x==='string'&&x.trim()).map(x=>x.trim()):[];
  if(id==='zip') return [];
  if(id==='pinpoint') return supplied.length===5?supplied:[];
  if(id==='crossclimb') return supplied.length===5?supplied:[];
  if(id==='queens' && supplied.length) return supplied.slice(0,3);
  if(id==='patches') {
    const rects=Array.isArray(a.rects)?a.rects:[];
    if(!rects.length)return [];
    const p=rects[0], area=x=>(x[2]-x[0]+1)*(x[3]-x[1]+1);
    const biggest=[...rects].sort((x,y)=>area(y)-area(x))[0];
    return [
      `A ${area(p)}-cell patch starts at row ${p[0]}, column ${p[1]}.`,
      `One of the largest patches covers ${area(biggest)} cells.`,
      `Try placing a ${biggest[2]-biggest[0]+1}×${biggest[3]-biggest[1]+1} patch beginning at row ${biggest[0]}, column ${biggest[1]}.`
    ];
  }
  if(id==='wordle'){
    const w=String(a.value||'').toUpperCase();
    if(!/^[A-Z]{5}$/.test(w)) return [];
    const vowels=[...w].filter(ch=>'AEIOU'.includes(ch)).length;
    return [`The answer begins with ${w[0]}.`,`It contains ${vowels} vowel${vowels===1?'':'s'} (A, E, I, O or U).`,`Its final letter is ${w[4]}.`];
  }
  if(id==='wend'){
    const words=Array.isArray(a.words)?a.words:[];
    return words.map((w,i)=>`Word ${i+1} begins with ${String(w)[0]} (${String(w).length} letters).`);
  }
  if(id==='tango'){
    const rows=a.rows;
    return Array.isArray(rows)&&rows.length>=4?[[1,1],[2,4],[4,3]].map(([r,c])=>`Row ${r}, column ${c} is ${rows[r-1][c-1]==='M'?'a moon':'a sun'}.`):[];
  }
  if(id==='mini-sudoku'){
    const rows=a.rows;
    return Array.isArray(rows)&&rows.length>=6?[[1,1],[3,4],[6,6]].map(([r,c])=>`Row ${r}, column ${c} contains ${rows[r-1][c-1]}.`):[];
  }
  if(id==='strands'){
    const hints=[];
    if(a.theme)hints.push(`The theme is “${a.theme}”.`);
    if(a.spangram)hints.push(`The spangram begins with ${a.spangram[0]}.`);
    if(a.paths?.[a.spangram]?.[0]) {
      const [r,c]=a.paths[a.spangram][0];
      hints.push(`Start tracing the spangram from row ${r}, column ${c}.`);
    }
    return hints;
  }
  if(id==='queens'){
    const cols=a.cols;
    if(!Array.isArray(cols))return [];
    return [
      `Try row 1, column ${cols[0]} as a starting placement.`,
      `The queen in row 2 goes in column ${cols[1]}.`,
      `The queen in the final row goes in column ${cols.at(-1)}.`
    ];
  }
  if(id==='mathler'){
    const expr=String(a.value||a.equation||'');
    const hints=[];
    if(a.target!==undefined)hints.push(`Today's target is ${a.target}.`);
    if(expr)hints.push(`The first character is ${expr[0]}.`);
    const op=expr.match(/[+\-*/]/);
    if(op)hints.push(`One operator is ${op[0]}.`);
    return hints;
  }
  if(id==='sumplete'){
    const k=a.kept;
    if(!Array.isArray(k)||!k.length)return [];
    return [`The number in row 1, column 1 is ${k[0][0]?'kept':'deleted'}.`,
      `Row 1 keeps ${k[0].filter(Boolean).length} number${k[0].filter(Boolean).length===1?'':'s'}.`,
      `Row 2 keeps ${k[1].filter(Boolean).length} numbers.`];
  }
  return supplied;
}

function dphClueBase(g,hints){
  if(!hints.length)return '';
  const shown=Math.min(clueLevels.get(g.id)||0,hints.length);
  const isPin=g.id==='pinpoint', isCross=g.id==='crossclimb';
  const heading=isPin?'REVEAL THE FIVE WORDS':isCross?'WORD CLUES':'NEED A CLUE?';
  const lines=hints.slice(0,shown).map((h,i)=>`<div class="dph-hint-row"><span class="dph-hint-number">${i+1}</span><span>${esc(h)}</span></div>`).join('');
  return `<section class="clue-panel dph-clue-panel" aria-label="Optional clues for ${esc(g.title)}">
    <div class="clue-panel-head"><span>${heading}</span><small>${shown} / ${hints.length} shown</small></div>
    ${lines}
    <div class="clue-buttons">
      ${shown<hints.length?`<button type="button" class="clue-next" data-clue="${esc(g.id)}" data-clue-action="next">${isPin?'Reveal word':isCross?'Reveal word clue':'Reveal clue'} ${shown+1}</button>`:'<span class="clue-complete">All clues revealed</span>'}
      ${shown>0?`<button type="button" class="clue-reset" data-clue="${esc(g.id)}" data-clue-action="reset">Hide clues</button>`:''}
    </div>
  </section>`;
}

function dphLadderProgress(a){
  const words=Array.isArray(a.words)?a.words:[];
  if(words.length!==7)return '';
  const n=Math.min(dphProgress.get('crossclimb')||0,words.length);
  const cells=words.map((word,i)=>{
    const visible=i<n;
    const letters=String(word).split('').map(ch=>`<span class="dph-rung-cell">${visible?esc(ch):''}</span>`).join('');
    return `<div class="dph-rung"><small>${i===0?'TOP WORD':i===6?'BOTTOM WORD':`RUNG ${i}`}</small><div class="dph-rung-letters ${visible?'is-visible':''}">${letters}</div></div>`;
  }).join('');
  return `<section class="dph-progress"><h4>Reveal the ladder</h4><p class="answer-desc">Uncover one rung at a time, without showing the whole solution.</p>${cells}
    <div class="dph-progress-actions">${n<words.length?'<button type="button" data-dph-progress="crossclimb" data-progress-action="next">Reveal next rung</button>':''}
      ${n>0?'<button type="button" data-dph-progress="crossclimb" data-progress-action="reset">Start over</button>':''}</div>
    <small>${n} of ${words.length} rungs revealed</small></section>`;
}

function dphPatchesProgress(a){
  const rects=Array.isArray(a.rects)?a.rects:[];
  if(!rects.length)return '';
  const side=Math.max(...rects.map(rect=>Math.max(rect[2],rect[3])));
  const n=Math.min(dphProgress.get('patches')||0,rects.length);
  const palette=['#efd6cd','#cde5f4','#d4ebd4','#f4dfb0','#dfcff0','#d2eae4','#f0c8dc','#e6e0c9','#cce6df','#e6d4c3','#cde8ab','#e1dce9'];
  const overlays=rects.slice(0,n).map((v,i)=>{
    const [r1,c1,r2,c2]=v,area=(r2-r1+1)*(c2-c1+1);
    return `<div class="dph-patch-overlay" style="grid-row:${r1}/${r2+1};grid-column:${c1}/${c2+1};background:${palette[i%palette.length]}">${area}</div>`;
  }).join('');
  return `<section class="dph-progress"><h4>Reveal the patches</h4><p class="answer-desc">Show one rectangular area at a time.</p>
    <div class="dph-patch-grid" style="grid-template-columns:repeat(${side},1fr);grid-template-rows:repeat(${side},1fr);background-size:calc(100% / ${side}) calc(100% / ${side})">${overlays}</div>
    <div class="dph-progress-actions">${n<rects.length?'<button type="button" data-dph-progress="patches" data-progress-action="next">Reveal next patch</button>':''}
      ${n>0?'<button type="button" data-dph-progress="patches" data-progress-action="reset">Start over</button>':''}</div>
    <small>${n} of ${rects.length} patches revealed</small></section>`;
}

function dphClueCard(g,d){
  if(!g||!d||d.status!=='verified')return '';
  if(g.id==='zip')return '';
  const hints=dphClues(g,d);
  const cluePanel=dphClueBase(g,hints);
  if(g.id==='crossclimb')return cluePanel+dphLadderProgress(d.answer||{});
  if(g.id==='patches')return cluePanel+dphPatchesProgress(d.answer||{});
  return cluePanel;
}

/* Draw NYT-style circular Strands trails. Do not synthesize a grid. */
function dphStrands(a){
  const title=`<p class="answer-desc">THEME · ${esc(a.theme||'')}</p>`;
  const words=[...(a.words||[]),a.spangram].filter(Boolean);
  const list=`<div class="answer-tag-row">${words.map((w,i)=>`<span class="answer-tag" style="background:${i===words.length-1?'#ffe29b':'#d6f2fa'}">${esc(w)}</span>`).join('')}</div>`;
  const grid=a.grid;
  if(!Array.isArray(grid)||grid.length!==8||!grid.every(row=>Array.isArray(row)&&row.length===6))
    return title+list+'<p class="answer-desc">A confirmed letter grid is not available for this date.</p>';
  const paths=a.paths||{};
  const used=new Set();
  const lines=[], disks=[];
  const point=([r,c])=>[(c-.5)*100,(r-.5)*100];
  const blues=['#a9dcec','#a8deec','#b0e2ed','#9fd6e7','#b3dfea','#a4d5e5','#a9dce8'];
  words.forEach((word,i)=>{
    const path=paths[word];
    if(!Array.isArray(path)||path.length!==word.length)return;
    const color=(i===words.length-1)?'#ffcc32':blues[i%blues.length];
    lines.push(`<polyline points="${path.map(p=>point(p).join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="75" stroke-linecap="round" stroke-linejoin="round"/>`);
    path.forEach(([r,c])=>{used.add(`${r},${c}`);const [x,y]=point([r,c]);disks.push(`<circle cx="${x}" cy="${y}" r="37" fill="${color}"/>`);});
  });
  const cells=grid.flatMap((row,r)=>row.map((letter,c)=>{
    const x=(c+.5)*100,y=(r+.5)*100;
    const filled=used.has(`${r+1},${c+1}`);
    return `${!filled?`<circle cx="${x}" cy="${y}" r="37" fill="#eaf4f7" stroke="#c6dfe6" stroke-width="1.5"/>`:''}<text x="${x}" y="${y+2}" text-anchor="middle" dominant-baseline="middle" fill="#143442" font-size="41" font-weight="700">${esc(letter)}</text>`;
  })).join('');
  return title+`<div class="dph-native-strands"><svg viewBox="0 0 600 800" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Solved Strands letter grid with blue theme-word trails and yellow spangram">${lines.join('')}${disks.join('')}${cells}</svg></div>`+list+`<p class="answer-desc">${used.size===48?'All answer words are traced in blue, with the spangram in yellow.':'The available word paths are highlighted. Unverified paths are not drawn.'}</p>`;
}

function cardHTML(g){const d=dayData?.games?.[g.id];const status=gameStatus(d);const saved=favourites.includes(g.id),isRevealed=revealed.has(g.id);const number=d?.number?esc(d.number):'Awaiting answer';let answer='';if(isRevealed)answer=`<div class="answer-area"><div class="answer-label">${d?.status==='verified'?'THE ANSWER':'WHAT WE KNOW'}</div>${answerHTML(d?.answer,g)}${d?.status==='example'?'<p class="answer-desc">Example, not an independently verified daily solution.</p>':''}</div>`;
 const source=d?.source?`<a href="${esc(safeExternal(d.source))}" target="_blank" rel="noopener noreferrer">View source ↗</a>`:'<span style="font-size:10px;color:#97a69e">No checked source for this date</span>';
 const hints=d?.hint?.length?`<details class="hint-details"><summary>Need a hint instead?</summary><ol class="hint-list">${d.hint.map(h=>`<li>${esc(h)}</li>`).join('')}</ol></details>`:'';
 const clueSection=dphClueCard(g,d);const other=g.id==='crosswordle'?`<a href="https://www.wordunscrambler.net/crosswordle-solver/" target="_blank" rel="noopener noreferrer">Open daily grid solver ↗</a>`:g.id==='mathler'?`<a href="https://www.fiveletterwords.io/mathler-solver" target="_blank" rel="noopener noreferrer">Open Mathler helper ↗</a>`:g.id==='wend'?`<a href="https://www.thewordfinder.com/linkedin-games-hub/wend-hints/" target="_blank" rel="noopener noreferrer">Open full Wend grid ↗</a>`:'';
 return `<article class="game-card" data-game="${esc(g.id)}"><div class="card-top"><div class="game-identity"><div class="game-icon ${g.colour}" aria-hidden="true">${esc(g.icon)}</div><div><h3 class="game-title">${esc(g.title)}</h3><div class="game-type">${esc(g.kind)}</div></div></div><button class="save-btn ${saved?'is-saved':''}" type="button" data-save="${g.id}" aria-label="${saved?'Remove':'Add'} ${g.title} ${saved?'from':'to'} favourites" aria-pressed="${saved}">${saved?'★':'☆'}</button></div><p class="card-desc">${esc(g.desc)}</p><div class="card-meta"><span class="card-number">${number}</span><span class="card-status ${status.cls}">${status.label}</span></div>${clueSection}<div class="card-actions"><button class="reveal-button" type="button" data-reveal="${g.id}" aria-expanded="${isRevealed}" ${!d||d.status==='missing'?'disabled title="No checked answer for this date"':''}>${isRevealed?'Hide answer ↑':d?.status==='verified'?'Reveal answer ↓':d?.status==='missing'||!d?'Awaiting answer':'View guide ↓'}</button><a class="play-button" href="${esc(safeExternal(g.play))}" target="_blank" rel="noopener noreferrer" aria-label="Play ${esc(g.title)} on the original website">Play ↗</a></div>${answer}<div class="source-row">${source}${other}</div></article>`;
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
  case 'strands':return dphStrands(a);
  case 'words':return g.id==='wend'?dphWend(a):`<div class="answer-tag-row">${a.words.map(w=>`<span class="answer-tag">${esc(w)}</span>`).join('')}</div>`;
  case 'ladder':return `<div class="answer-ladder">${a.words.map(w=>`<span>${esc(w)}</span>`).join('')}</div><p class="answer-desc">${esc(a.description||'')}</p>`;
  case 'queens':return dphQueensPhase2(a);
  case 'crosswordle':return dphCrosswordle(a);
  case 'sudoku':return gridHTML(a.rows,'sudoku-board');
  case 'tango':return gridHTML(a.rows,'tango-board',(_r,_c,v)=>v==='M'?'moon':'',(_r,_c,v)=>v==='M'?'☾':'☀');
  case 'zip':return dphZip(a);
  case 'patches':{const side=Math.max(...a.rects.map(rect=>Math.max(rect[2],rect[3])));const matrix=Array.from({length:side},()=>Array(side).fill(null));a.rects.forEach(([r1,c1,r2,c2],index)=>{for(let r=r1;r<=r2;r++)for(let c=c1;c<=c2;c++)matrix[r-1][c-1]={index,label:r===r1&&c===c1?(r2-r1+1)*(c2-c1+1):''}});const colours=['#dceaf8','#e8d9ed','#c8e6e3','#fce9bd','#f2c6be','#e8e7bd','#d5edc6','#fae1b3','#d6def5','#fbd9e9','#c4e7ef','#d7eaca','#ecddc5','#e0e2ed'];return gridHTML(matrix,'patches-board',()=>'',(_r,_c,v)=>`<span style="background:${colours[v?.index%colours.length]};width:100%;height:100%;border-radius:3px;display:grid;place-items:center">${v?.label||''}</span>`)+'<p class="answer-desc">Each colour is a rectangle. Numbers indicate patch area in cells.</p>'}
  case 'sumplete':{let out='<div class="sumplete-table">';for(let r=0;r<5;r++){for(let c=0;c<5;c++)out+=`<div class="board-cell ${a.kept[r][c]?'keep':'delete'}"><span class="sumplete-num">${esc(a.grid[r][c])}</span></div>`;out+=`<div class="board-cell target">${esc(a.rowTargets[r])}</div>`}for(let c=0;c<5;c++)out+=`<div class="board-cell target">${esc(a.colTargets[c])}</div>`;out+='<div class="board-cell target">✓</div></div><p class="answer-desc">Green = keep · Red crossed out = delete · Targets shown on the right and bottom.</p>';return out}
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
document.addEventListener('click',event=>{const filter=event.target.closest('[data-filter]');if(filter){setFilter(filter.dataset.filter);return}const pb=event.target.closest('[data-dph-progress]');if(pb){const id=pb.dataset.dphProgress;if(pb.dataset.progressAction==='reset')dphProgress.delete(id);else dphProgress.set(id,(dphProgress.get(id)||0)+1);render();return;}const cb=event.target.closest('[data-clue]');if(cb){const id=cb.dataset.clue;const g=GAMES.find(g=>g.id===id);const max=dphClues(g,dayData?.games?.[id]).length;if(cb.dataset.clueAction==='reset')clueLevels.delete(id);else clueLevels.set(id,Math.min(max,(clueLevels.get(id)||0)+1));render();return;}const btn=event.target.closest('[data-reveal]');if(btn){if(revealed.has(btn.dataset.reveal))revealed.delete(btn.dataset.reveal);else revealed.add(btn.dataset.reveal);render();return}const save=event.target.closest('[data-save]');if(save){const id=save.dataset.save;favourites=favourites.includes(id)?favourites.filter(x=>x!==id):[...favourites,id];storage.set('dph:favourites',favourites);render();return}});
$('search-input').addEventListener('input',event=>{searchText=event.target.value.trim().toLowerCase();render()});
$('date-input').addEventListener('change',event=>selectDate(event.target.value));
$('prev-day').addEventListener('click',()=>selectDate(addDays(selectedDay,-1)));
$('next-day').addEventListener('click',()=>selectDate(addDays(selectedDay,1)));
$('today-button').addEventListener('click',()=>selectDate(ukToday()));
$('theme-toggle').addEventListener('click',()=>{document.body.classList.toggle('dark');storage.set('dph:dark',document.body.classList.contains('dark'));$('theme-toggle').textContent=document.body.classList.contains('dark')?'☀':'☾'});
if(storage.get('dph:dark',false)){document.body.classList.add('dark');$('theme-toggle').textContent='☀'}
$('footer-year').textContent=String(new Date().getFullYear());
selectDate(ukToday());
