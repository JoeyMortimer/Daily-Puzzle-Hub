'use strict';
const GAMES = [
 {id:'wordle',title:'Wordle',category:'nyt',kind:'WORD GAME',icon:'W',colour:'green',desc:'The world’s favourite five-letter daily guessing game.',play:'https://www.nytimes.com/games/wordle/index.html'},
 {id:'strands',title:'Strands',category:'nyt',kind:'WORD SEARCH',icon:'S',colour:'blue',desc:'Find all the themed words and the hidden spangram.',play:'https://www.nytimes.com/games/strands'},
 {id:'crosswordle',title:'Crosswordle',category:'nyt',kind:'WORD LOGIC',icon:'C',colour:'purple',desc:'Reverse-Wordle: build guesses to fit coloured clues.',play:'https://crosswordle.vercel.app/'},
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
  if(embedded && day===embedded.date){dayData=embedded;render();return}
  try{const response=await fetch(`data/${day}.json`,{cache:'no-store'});if(!response.ok)throw new Error('No daily data');const found=await response.json();if(found.date!==day)throw new Error('Wrong date');if(selectedDay!==snapshot)return;dayData=found}
  catch(_){if(selectedDay!==snapshot)return;dayData={date:day,games:{}};notice.textContent=`We don't have checked answers for ${prettyDate(day)} yet. You can still open each game or its answer-source link. We never display an older puzzle as today's answer.`;notice.hidden=false}
  render();
}
function gameStatus(d){if(!d)return {label:'NOT YET VERIFIED',cls:'missing'};if(d.status==='verified')return {label:'✓ ANSWER VERIFIED',cls:''};if(d.status==='missing')return {label:'NOT YET VERIFIED',cls:'missing'};if(d.status==='example')return {label:'EXAMPLE ONLY',cls:'example'};return {label:'GUIDE AVAILABLE',cls:'guide'}}
function cardHTML(g){const d=dayData?.games?.[g.id];const status=gameStatus(d);const saved=favourites.includes(g.id),isRevealed=revealed.has(g.id);const number=d?.number?esc(d.number):'Awaiting answer';let answer='';if(isRevealed)answer=`<div class="answer-area"><div class="answer-label">${d?.status==='verified'?'THE ANSWER':'WHAT WE KNOW'}</div>${answerHTML(d?.answer,g)}${d?.status==='example'?'<p class="answer-desc">Example, not an independently verified daily solution.</p>':''}</div>`;
 const source=d?.source?`<a href="${esc(safeExternal(d.source))}" target="_blank" rel="noopener noreferrer">View source ↗</a>`:'<span style="font-size:10px;color:#97a69e">No checked source for this date</span>';
 const hints=d?.hint?.length?`<details class="hint-details"><summary>Need a hint instead?</summary><ol class="hint-list">${d.hint.map(h=>`<li>${esc(h)}</li>`).join('')}</ol></details>`:'';
 const other=g.id==='crosswordle'?`<a href="https://crosswordle.com/" target="_blank" rel="noopener noreferrer">Swap-based variant ↗</a>`:'';
 return `<article class="game-card" data-game="${esc(g.id)}"><div class="card-top"><div class="game-identity"><div class="game-icon ${g.colour}" aria-hidden="true">${esc(g.icon)}</div><div><h3 class="game-title">${esc(g.title)}</h3><div class="game-type">${esc(g.kind)}</div></div></div><button class="save-btn ${saved?'is-saved':''}" type="button" data-save="${g.id}" aria-label="${saved?'Remove':'Add'} ${g.title} ${saved?'from':'to'} favourites" aria-pressed="${saved}">${saved?'★':'☆'}</button></div><p class="card-desc">${esc(g.desc)}</p><div class="card-meta"><span class="card-number">${number}</span><span class="card-status ${status.cls}">${status.label}</span></div><div class="card-actions"><button class="reveal-button" type="button" data-reveal="${g.id}" aria-expanded="${isRevealed}" ${!d||d.status==='missing'?'disabled title="No checked answer for this date"':''}>${isRevealed?'Hide answer ↑':d?.status==='verified'?'Reveal answer ↓':d?.status==='missing'||!d?'Awaiting answer':'View guide ↓'}</button><a class="play-button" href="${esc(safeExternal(g.play))}" target="_blank" rel="noopener noreferrer" aria-label="Play ${esc(g.title)} on the original website">Play ↗</a></div>${hints}${answer}<div class="source-row">${source}${other}</div></article>`;
}
function gridHTML(rows,cls,extraClass=(r,c,v)=>'',renderCell=(r,c,v)=>esc(v)){const cols=rows[0]?.length||0;return `<div class="game-board ${cls}" style="grid-template-columns:repeat(${cols},minmax(0,1fr))">${rows.map((row,r)=>row.map((v,c)=>`<div class="board-cell ${extraClass(r,c,v)}" aria-label="Row ${r+1}, column ${c+1}: ${esc(v)}">${renderCell(r,c,v)}</div>`).join('')).join('')}</div>`}
function answerHTML(a,g){if(!a)return `<p class="answer-desc">Not verified for this date. Choose “Play” to open the game.</p>`;
 switch(a.type){
  case 'word':return `<div class="answer-word">${esc(a.value)}</div>`;
  case 'strands':return `<div class="answer-desc">THEME · ${esc(a.theme)}</div><p class="answer-desc">SPANGRAM</p><div class="answer-word">${esc(a.spangram)}</div><p class="answer-desc">THEME WORDS</p><div class="answer-tag-row">${a.words.map(w=>`<span class="answer-tag">${esc(w)}</span>`).join('')}</div>`;
  case 'words':return `<div class="answer-tag-row">${a.words.map(w=>`<span class="answer-tag">${esc(w)}</span>`).join('')}</div>`;
  case 'ladder':return `<div class="answer-ladder">${a.words.map(w=>`<span>${esc(w)}</span>`).join('')}</div><p class="answer-desc">${esc(a.description||'')}</p>`;
  case 'queens':{const grid=a.cols.map((col,r)=>Array.from({length:a.cols.length},(_,c)=>(c+1===col)?'♛':'·'));return gridHTML(grid,'queens-board',(r,c,v)=>v==='♛'?'queen':'',(_r,_c,v)=>v==='♛'?'♛':'')+`<p class="answer-desc">Columns by row: ${esc(a.cols.join(', '))}.</p>`}
  case 'sudoku':return gridHTML(a.rows,'sudoku-board');
  case 'tango':return gridHTML(a.rows,'tango-board',(_r,_c,v)=>v==='M'?'moon':'',(_r,_c,v)=>v==='M'?'☾':'☀');
  case 'zip':{const matrix=Array.from({length:8},()=>Array(8).fill(''));a.path.forEach(([r,c],i)=>{if(matrix[r-1])matrix[r-1][c-1]=i+1});return gridHTML(matrix,'zip-board',(_r,_c,v)=>v===1?'start':v===64?'end':'')+'<p class="answer-desc">Numbers show the step order through all 64 cells. Start at 1, finish at 64.</p>'}
  case 'patches':{const matrix=Array.from({length:8},()=>Array(8).fill(null));a.rects.forEach(([r1,c1,r2,c2],index)=>{for(let r=r1;r<=r2;r++)for(let c=c1;c<=c2;c++)matrix[r-1][c-1]={index,label:r===r1&&c===c1?(r2-r1+1)*(c2-c1+1):''}});const colours=['#dceaf8','#e8d9ed','#c8e6e3','#fce9bd','#f2c6be','#e8e7bd','#d5edc6','#fae1b3','#d6def5','#fbd9e9','#c4e7ef','#d7eaca','#ecddc5','#e0e2ed'];return gridHTML(matrix,'patches-board',()=>'',(_r,_c,v)=>`<span style="background:${colours[v?.index%colours.length]};width:100%;height:100%;border-radius:3px;display:grid;place-items:center">${v?.label||''}</span>`)+'<p class="answer-desc">Each colour is a rectangle. Numbers indicate patch area in cells.</p>'}
  case 'sumplete':{let out='<div class="sumplete-table">';for(let r=0;r<5;r++){for(let c=0;c<5;c++)out+=`<div class="board-cell ${a.kept[r][c]?'keep':'delete'}">${esc(a.grid[r][c])}</div>`;out+=`<div class="board-cell target">${esc(a.rowTargets[r])}</div>`}for(let c=0;c<5;c++)out+=`<div class="board-cell target">${esc(a.colTargets[c])}</div>`;out+='<div class="board-cell target">✓</div></div><p class="answer-desc">Green = keep · Red crossed out = delete · Targets shown on the right and bottom.</p>';return out}
  case 'math':return `<div class="math-answer">${esc(a.value)} = 2</div><p class="answer-desc">${esc(a.description||'')}</p>`;
  case 'notice':return `<strong class="answer-word" style="font-size:17px">${esc(a.title)}</strong><p class="answer-desc">${esc(a.value)}</p>`;
  default:return '<p class="answer-desc">No compatible answer format.</p>';
 }
}
function render(){const visible=GAMES.filter(g=>(activeFilter==='all'||g.category===activeFilter||(activeFilter==='favourites'&&favourites.includes(g.id)))&&(`${g.title} ${g.desc} ${g.kind}`.toLowerCase().includes(searchText)));
 visible.sort((a,b)=>Number(favourites.includes(b.id))-Number(favourites.includes(a.id))||GAMES.indexOf(a)-GAMES.indexOf(b));$('cards').innerHTML=visible.map(cardHTML).join('');$('game-count').textContent=visible.length;$('empty-search').hidden=!!visible.length;const verified=GAMES.filter(g=>dayData?.games?.[g.id]?.status==='verified').length;$('date-subtitle').textContent=`${verified} checked solutions · ${GAMES.length} games in one place.`;document.querySelectorAll('[data-filter]').forEach(el=>{const active=el.dataset.filter===activeFilter;el.classList.toggle('active',active);if(el.tagName==='BUTTON')el.setAttribute('aria-pressed',String(active))})}
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
