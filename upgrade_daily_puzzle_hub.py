#!/usr/bin/env python3
"""Daily Puzzle Hub: reliable Sudoku boxes + future Crosswordle grid support."""
from pathlib import Path
import re
p=Path.cwd()
cssf=p/'style.css'; jsf=p/'app.js'; htmlf=p/'index.html'
for f in (cssf,jsf,htmlf):
 if not f.is_file():raise SystemExit(f'Missing {f}: run from repo root')
css=cssf.read_text(); js=jsf.read_text(); html=htmlf.read_text()
css=re.sub(r'/\* Mini Sudoku: six 2x3 boxes \*/.*?(?=\n/\*|\Z)','',css,flags=re.S)
if '/* SUDOKU-SUBGRID-V5 */' not in css:
 css+='''
/* SUDOKU-SUBGRID-V5 */
.game-card[data-game="mini-sudoku"] .sudoku-board{gap:0!important;border:3px solid #29463d!important;border-radius:2px;overflow:hidden;box-shadow:none!important}
.game-card[data-game="mini-sudoku"] .sudoku-board::after{display:none!important;content:none!important}
.game-card[data-game="mini-sudoku"] .sudoku-board>.board-cell{background:#f8fbf8;border:0!important;border-radius:0!important;border-right:1px solid #a9bdb1!important;border-bottom:1px solid #a9bdb1!important;box-shadow:none!important;font-size:clamp(13px,2vw,18px)}
.game-card[data-game="mini-sudoku"] .sudoku-board>.board-cell:nth-child(6n + 3){border-right:3px solid #29463d!important}
.game-card[data-game="mini-sudoku"] .sudoku-board>.board-cell:nth-child(n + 13):nth-child(-n + 18),.game-card[data-game="mini-sudoku"] .sudoku-board>.board-cell:nth-child(n + 25):nth-child(-n + 30){border-top:3px solid #29463d!important}
.game-card[data-game="mini-sudoku"] .sudoku-board>.board-cell:nth-child(6n){border-right:0!important}
body.dark .game-card[data-game="mini-sudoku"] .sudoku-board>.board-cell{background:#284239!important;color:#eaf8ee!important}
.crosswordle-board{gap:0;border:2px solid #29463d}.crosswordle-board .board-cell{border:1px solid #a9bdb1;border-radius:0;background:#fafcfa}.crosswordle-board .board-cell.wall{background:#29463d}
'''
if '/* CROSSWORDLE-BOARD-V1 */' not in js:
 old='function answerHTML(a,g)'
 if js.count(old)!=1:raise SystemExit('answerHTML changed')
 func='''/* CROSSWORDLE-BOARD-V1 */
function dphCrosswordle(a){const rows=a.rows;
 if(!Array.isArray(rows)||![7,9].includes(rows.length)||!rows.every(row=>Array.isArray(row)&&row.length===rows.length&&row.every(ch=>typeof ch==='string'&&(ch==='#'||/^[A-Z]$/i.test(ch)))))return '<p class="answer-desc">No verified completed Crosswordle board available.</p>';
 return gridHTML(rows,'crosswordle-board',(_r,_c,v)=>v==='#'?'wall':'',(_r,_c,v)=>v==='#'?'':esc(v.toUpperCase()));}
'''
 js=js.replace(old,func+old,1)
 sw="case 'sudoku':return"
 if js.count(sw)!=1:raise SystemExit('Sudoku switch changed')
 js=js.replace(sw,"case 'crosswordle':return dphCrosswordle(a);\n  "+sw,1)
# Add optional date-matched answer imports, preserving the existing importer.
up=p/'scripts/update.py'
if not up.is_file():raise SystemExit('scripts/update.py missing')
original=up.read_text()
if '# DPH-OPTIONAL-DAILY-IMPORTS-V1' not in original:
    anchor='def update(day,force=False):'
    if original.count(anchor)!=1:raise SystemExit('Updater entry point changed')
    original=original.replace(anchor,'# DPH-OPTIONAL-DAILY-IMPORTS-V1\n# Do not manufacture solutions: this requires a date-matched published source.\nimport ast\nfrom fractions import Fraction\n\ndef checked_mathler(day, out):\n    url=\'https://www.gfinityesports.com/article/answer-solution\'\n    raw=fetch(url)\n    if not raw:return\n    soup=BeautifulSoup(raw,\'html.parser\')\n    for el in soup([\'script\',\'style\',\'nav\',\'footer\']):el.decompose()\n    headings=\' \'.join(x.get_text(\' \',strip=True) for x in soup.find_all([\'h1\',\'h2\']))\n    text=soup.get_text(\' \',strip=True)\n    stamp=f\'{day.strftime("%B")} {day.day}\'\n    if f\'Mathler Answer Today ({stamp})\'.lower() not in headings.lower():return\n    if not re.search(rf\'(?:Updated|Last Verified)\\s*:?\\s*{re.escape(stamp)},?\\s*{day.year}\',text,re.I):return\n    match=re.search(r\'Today.s normal Mathler solution is\\s*([0-9+*/-]{6})\\b\',text,re.I)\n    if not match:return\n    expression=match.group(1)\n    def evaluate(node):\n        if isinstance(node,ast.Expression):return evaluate(node.body)\n        if isinstance(node,ast.Constant) and type(node.value)==int and 0<=node.value<=999:return Fraction(node.value)\n        if isinstance(node,ast.BinOp):\n            left,right=evaluate(node.left),evaluate(node.right)\n            if isinstance(node.op,ast.Add):return left+right\n            if isinstance(node.op,ast.Sub):return left-right\n            if isinstance(node.op,ast.Mult):return left*right\n            if isinstance(node.op,ast.Div):return left/right\n        raise ValueError(\'Unsupported expression\')\n    try:result=evaluate(ast.parse(expression,mode=\'eval\'))\n    except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):return\n    if result.denominator!=1 or not 0<=result<=100000:return\n    out[\'games\'][\'mathler\']={\'status\':\'verified\',\'number\':\'Normal\',\'hint\':[],\n        \'answer\':{\'type\':\'math\',\'value\':expression,\'target\':int(result),\'description\':\'Published independently for this exact date.\'},\'source\':url}\n    print(\'  ✓ mathler: dated independent answer\')\n\ndef checked_wend_board(day,out):\n    entry=out[\'games\'].get(\'wend\')\n    if not entry or entry.get(\'status\')!=\'verified\':return\n    words=entry[\'answer\'].get(\'words\',[])\n    number=BASE_NUM[\'wend\']+(day-BASE).days\n    url=\'https://hintsheet.com/wend/answer-today\'\n    raw=fetch(url)\n    if not raw:return\n    soup=BeautifulSoup(raw,\'html.parser\')\n    for el in soup([\'script\',\'style\',\'nav\',\'footer\']):el.decompose()\n    text=soup.get_text(\' \',strip=True)\n    # Source heading must say the requested date AND requested puzzle number.\n    stamp=f\'{day.strftime("%b")} {day.day}, {day.year}\'\n    if stamp.lower() not in text.lower() or not re.search(rf\'Wend\\s*#\\s*{number}\\b\',text,re.I):return\n    match=re.search(r\'Step.by.step walkthrough(.+?)(?:Full solution|How a Wend|Frequently Asked|$)\',text,re.I|re.S)\n    if not match:return\n    section=match.group(1)\n    paths=[]\n    for word in words:\n        pat=rf\'\\b{re.escape(word)}\\s*[—–:-]\\s*((?:R\\d+C\\d+\\s*(?:→|->)\\s*)*R\\d+C\\d+)\'\n        found=re.search(pat,section,re.I)\n        if not found:return\n        pos=[list(map(int,xy)) for xy in re.findall(r\'R(\\d+)C(\\d+)\',found.group(1),re.I)]\n        if len(pos)!=len(word):return\n        paths.append(pos)\n    used={};limit=0\n    for word,path in zip(words,paths):\n        for i,(r,c) in enumerate(path):\n            if (r,c) in used:return\n            used[(r,c)]=word[i].upper()\n            limit=max(limit,r,c)\n        if any(abs(a[0]-b[0])+abs(a[1]-b[1])!=1 for a,b in zip(path,path[1:])):return\n    size=re.search(r\'\\b([5-9])\\s*[x×]\\s*\\1\\b\',text)\n    n=int(size.group(1)) if size else limit\n    if not 5<=n<=9 or limit>n:return\n    grid=[[\'#\']*n for _ in range(n)]\n    for (r,c),letter in used.items():grid[r-1][c-1]=letter\n    entry[\'answer\'].update({\'grid\':grid,\'paths\':paths})\n    entry[\'boardSource\']=url\n    print(\'  ✓ wend: original grid and paths\')\n'+'\n'+anchor,1)
    hook='    update_linkedin(day,obj)'
    if original.count(hook)!=1:raise SystemExit('LinkedIn updater changed')
    original=original.replace(hook,hook+'\n    checked_wend_board(day,obj)\n    checked_mathler(day,obj)',1)
    original=original.replace('s,1,flags=re.I)', 's,maxsplit=1,flags=re.I)')
    # Keep the same-date verified Wend board if a source goes temporarily stale.
    needle="                        obj['games'][name]=old"
    if original.count(needle)==1:
        extra="\n                    elif name=='wend' and old.get('status')=='verified' and obj['games'].get(name,{}).get('status')=='verified':\n                        earlier=old.get('answer',{})\n                        current=obj['games'][name]['answer']\n                        if earlier.get('words')==current.get('words') and earlier.get('grid') and earlier.get('paths') and not current.get('grid'):\n                            current['grid']=earlier['grid']\n                            current['paths']=earlier['paths']"
        original=original.replace(needle,needle+extra,1)

    up.write_text(original)
    print('Updated scripts/update.py with optional checked imports')

# Validate optional complete Wend and Crosswordle boards.
vp=p/'scripts/validate.py'
if vp.is_file():
    validator=vp.read_text()
    if '# DPH-OPTIONAL-BOARD-VALIDATION-V1' not in validator:
        validator=validator.replace("SUPPORTED={'word'","SUPPORTED={'crosswordle','word'",1)
        key="    if t=='sumplete':"
        if validator.count(key)!=1:raise SystemExit('Validator layout changed')
        vp.write_text(validator.replace(key,"    # DPH-OPTIONAL-BOARD-VALIDATION-V1\n    if t=='crosswordle':\n        rows=a['rows'];n=len(rows)\n        assert n in (7,9) and all(len(row)==n for row in rows)\n        assert all(isinstance(ch,str) and (ch=='#' or len(ch)==1 and ch.isalpha()) for row in rows for ch in row)\n    if t=='words' and game_id=='wend' and ('paths' in a or 'grid' in a):\n        rows=a['grid']; paths=a['paths']; words=a['words']; n=len(rows)\n        assert 5<=n<=9 and all(len(row)==n for row in rows)\n        assert len(words)==len(paths)\n        used=[]\n        for word,path in zip(words,paths):\n            assert len(word)==len(path)\n            assert all(1<=r<=n and 1<=c<=n for r,c in path)\n            assert ''.join(rows[r-1][c-1] for r,c in path).upper()==word.upper()\n            assert all(abs(x[0]-y[0])+abs(x[1]-y[1])==1 for x,y in zip(path,path[1:]))\n            used.extend(tuple(x) for x in path)\n        assert len(used)==len(set(used))\n        assert set(used)=={(r+1,c+1) for r,row in enumerate(rows) for c,ch in enumerate(row) if ch not in ('#','',None)}\n"+key,1))
        print('Updated scripts/validate.py')
# Wend: when the daily grid coordinates are not yet imported, show a real-board reference.
if 'Open full Wend grid ↗' not in js:
    old="Open Mathler helper ↗</a>`:'';"
    new="Open Mathler helper ↗</a>`:g.id==='wend'?`<a href=\"https://www.thewordfinder.com/linkedin-games-hub/wend-hints/\" target=\"_blank\" rel=\"noopener noreferrer\">Open full Wend grid ↗</a>`:'';"
    if old in js:js=js.replace(old,new,1)
for asset in ('app.js','style.css'):
 html,n=re.subn(re.escape(asset)+r'(?:\?[^"\']*)?(?=["\'])',asset+'?v=sudoku-v5',html,count=1)
 if n!=1:raise SystemExit('Asset reference not found: '+asset)
cssf.write_text(css);jsf.write_text(js);htmlf.write_text(html)
print('Updated style.css, app.js, index.html')
print('Validate: node --check app.js && python scripts/validate.py && python scripts/embed.py')
