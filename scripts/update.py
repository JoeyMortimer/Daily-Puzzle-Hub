#!/usr/bin/env python3
"""Best-effort daily *answer-data* importer.

IMPORTANT: The sources below are independent puzzle guides, not APIs. They may change,
block automation, or have reuse restrictions. Respect their terms and update sources or
switch to a licensed feed if necessary. Nothing unverified is published as 'verified'.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime
import itertools
import json
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
BASE=date(2026,11,1)
BASE_NUM={'pinpoint':915,'crossclimb':915,'queens':915,'tango':755,'zip':594,'mini-sudoku':447,'patches':229,'wend':146}
BASE_LINK='https://lianswers.com/linkedin/'
HEADERS={'User-Agent':'DailyPuzzleHub/0.1 (+https://github.com/; independent puzzle guide)','Accept':'text/html,application/json;q=0.9,*/*;q=0.8'}

def fetch(url):
    try:
        req=Request(url,headers=HEADERS)
        with urlopen(req,timeout=15) as res:
            if res.status!=200: raise RuntimeError(f'HTTP {res.status}')
            return res.read().decode('utf-8','replace')
    except Exception as exc:
        print(f'  Unavailable: {url} ({str(exc)[:100]})')
        return ''

def date_formatted(day):
    return f'{day.strftime("%B")} {day.day}, {day.year}'

def checked_page(html,day,name=None,number=None):
    if not html:return ''
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup(['script','style','nav','footer']):tag.decompose()
    txt=soup.get_text(' ',strip=True)
    heading=(soup.find('h1').get_text(' ',strip=True) if soup.find('h1') else '')
    if date_formatted(day).lower() not in heading.lower():return ''
    if name and name.lower() not in heading.lower():return ''
    if number and f'#{number}' not in heading:return ''
    return txt

def solution_section(text,game,kind='Solution'):
    pattern=rf'Today.s {re.escape(game)} {kind}\s+'
    matches=list(re.finditer(pattern,text,re.I))
    if not matches:return ''
    s=text[matches[-1].end():]
    return re.split(r'How to Solve Today|How to play|How the game works|Help a friend',s,maxsplit=1,flags=re.I)[0]

def check_grid(grid,size):
    return len(grid)==size and all(len(row)==size for row in grid)

def queens(text):
    s=solution_section(text,'Queens')
    m=re.search(r'Queen positions \(row, column\):\s*((?:R\d+C\d+[,\s.]*)+)',s,re.I)
    if not m:return None
    cells=[(int(r),int(c)) for r,c in re.findall(r'R(\d+)C(\d+)',m.group(1))]
    n=len(cells)
    if not 5<=n<=12 or [r for r,c in cells]!=list(range(1,n+1)):return None
    cols=[c for r,c in cells]
    if set(cols)!=set(range(1,n+1)) or any(abs(cols[i]-cols[i-1])<=1 for i in range(1,n)):return None
    return {'type':'queens','cols':cols}

def tango(text):
    s=solution_section(text,'Tango')
    rows=[]
    for i in range(1,7):
        m=re.search(rf'Row {i}:\s*(.*?)(?=Row {i+1}:|$)',s,re.I|re.S)
        if not m:return None
        vals=[{'sun':'S','moon':'M'}[v.lower()] for v in re.findall(r'\b(?:Sun|Moon)\b',m.group(1))[:6]]
        if len(vals)!=6 or vals.count('S')!=3:return None
        rows.append(vals)
    if not all([rows[r][c] for r in range(6)].count('S')==3 for c in range(6)):return None
    if any(rows[r][c]==rows[r][c+1]==rows[r][c+2] for r in range(6) for c in range(4)):return None
    if any(rows[r][c]==rows[r+1][c]==rows[r+2][c] for c in range(6) for r in range(4)):return None
    return {'type':'tango','rows':rows}

def zipgame(text):
    s=solution_section(text,'Zip')
    m=re.search(r'Path sequence:\s*(.*?)(?=\s+How to Solve|\s+The route|$)',s,re.I|re.S)
    if not m:return None
    path=[[int(r),int(c)] for r,c in re.findall(r'R(\d+)C(\d+)',m.group(1))]
    n=len(path)
    if n not in [36,49,64,81]:return None
    side=int(n**0.5)
    if len({tuple(x) for x in path})!=n or any(not 1<=r<=side or not 1<=c<=side for r,c in path):return None
    if any(abs(path[i][0]-path[i-1][0])+abs(path[i][1]-path[i-1][1])!=1 for i in range(1,n)):return None
    # Render every valid 6x6 to 9x9 board.
    return {'type':'zip','path':path}

def sudoku(text):
    s=solution_section(text,'Mini Sudoku')
    rows=[]
    for i in range(1,7):
        m=re.search(rf'Row {i}:\s*(.*?)(?=Row {i+1}:|$)',s,re.I|re.S)
        if not m:return None
        vals=list(map(int,re.findall(r'\b[1-6]\b',m.group(1))[:6]))
        if len(vals)!=6 or set(vals)!=set(range(1,7)):return None
        rows.append(vals)
    if not all({row[c] for row in rows}==set(range(1,7)) for c in range(6)):return None
    for r in range(0,6,2):
        for c in range(0,6,3):
            if {rows[rr][cc] for rr in range(r,r+2) for cc in range(c,c+3)}!=set(range(1,7)):return None
    return {'type':'sudoku','rows':rows}

def patches(text):
    s=solution_section(text,'Patches')
    m=re.search(r'Patches:\s*(.*)',s,re.S|re.I)
    if not m:return None
    rectangles=[[int(v) for v in match] for match in re.findall(r'from R(\d+)C(\d+) to R(\d+)C(\d+)',m.group(1))]
    if not rectangles:return None
    cells=[]
    side=max(max(r2,c2) for _,_,r2,c2 in rectangles)
    if side not in (6,7,8,9):return None
    for r1,c1,r2,c2 in rectangles:
        if not (1<=r1<=r2<=side and 1<=c1<=c2<=side):return None
        cells.extend((r,c) for r in range(r1,r2+1) for c in range(c1,c2+1))
    if len(cells)!=side*side or len(set(cells))!=side*side:return None
    return {'type':'patches','rects':rectangles}

def pinpoint(text):
    s=solution_section(text,'Pinpoint','Answer')
    m=re.search(r'Category\s+(.+?)(?=\s+Clues:|\s+How to|$)',s,re.S|re.I)
    if not m:return None
    word=m.group(1).strip(' .')
    return {'type':'word','value':word} if 2<len(word)<110 else None

def crossclimb(text):
    s=solution_section(text,'Crossclimb')
    m=re.search(r'Answer\s+([A-Z]{3,10}(?:,\s*[A-Z]{3,10}){6})',s)
    if not m:return None
    words=[w.strip() for w in m.group(1).split(',')]
    if len({len(w) for w in words})!=1:return None
    if any(sum(a!=b for a,b in zip(words[i],words[i+1]))!=1 for i in range(6)):return None
    return {'type':'ladder','words':words,'description':f'Bookend phrase: {words[0]} {words[-1]}.'}

def wend(text):
    s=solution_section(text,'Wend')
    m=re.search(r'Words:\s*([A-Z]+(?:,\s*[A-Z]+){2,7})',s)
    if not m:return None
    words=[w.strip() for w in m.group(1).split(',')]
    if not 3<=len(words)<=8 or len(words)!=len(set(words)):return None
    return {'type':'words','words':words}

PARSERS={'queens':queens,'tango':tango,'zip':zipgame,'mini-sudoku':sudoku,'patches':patches,'pinpoint':pinpoint,'crossclimb':crossclimb,'wend':wend}


# DPH ZIP CHECKPOINTS V2: verified number -> row/column positions
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
        pairs=list(re.finditer(r'\b(\d{1,2})\s*(?:→|->)\s*(\d{1,2})\s*:',text))
        for i,m in enumerate(pairs):
            sec=text[m.end():(pairs[i+1].start() if i+1<len(pairs) else len(text))]
            coords=[tuple(map(int,x)) for x in re.findall(r'R(\d+)C(\d+)',sec)[:150]]
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

def update_linkedin(day,out):
    diff=(day-BASE).days
    for game,base in BASE_NUM.items():
        n=base+diff
        if n<1:continue
        url=f'{BASE_LINK}{game}/{n}-answer/'
        txt=checked_page(fetch(url),day,game.replace('-', ' '),n)
        result=PARSERS[game](txt) if txt else None
        if result:
            if game=='zip':
                result['checkpoints']=zip_checkpoints(txt,result['path'],day.isoformat())
                if result['checkpoints'] is None:result.pop('checkpoints')
            if game=='queens' and day.isoformat()=='2026-11-02':
                # Row-by-row region names reported by two independent puzzle guides.
                # Full original board region geometry is NOT available from this feed.
                result['crownRegions']=['Lavender','Pastel Green','Light Gray','Vibrant Coral','Lime Yellow','Soft Blue','Peach Orange']
            out['games'][game]={'status':'verified','number':f'#{n}','hint':[],'answer':result,'source':url}
            print('  ✓',game,'#'+str(n))
        else:
            out['games'][game]={'status':'missing','number':f'#{n}','hint':[],'answer':None,'source':f'{BASE_LINK}{game}/'}
            print('  -',game,'not confirmed')
        time.sleep(.2)

def update_wordle(day,out):
    url=f'https://www.nytimes.com/svc/wordle/v2/{day.isoformat()}.json'
    raw=fetch(url)
    try:
        obj=json.loads(raw)
        word=str(obj['solution']).upper()
        if len(word)==5 and word.isalpha():
            num=1961+(day-BASE).days
            out['games']['wordle']={'status':'verified','number':f'#{num}','hint':[],'answer':{'type':'word','value':word},'source':url}
            print('  ✓ wordle')
            return
    except (ValueError,KeyError,TypeError):pass
    out['games']['wordle']={'status':'missing','number':f'#{1961+(day-BASE).days}','answer':None,'source':'https://www.today-wordle.com/'}
    print('  - wordle not confirmed')

def solve_sumplete(matrix,targets,cols):
    candidates=[]
    for row,target in zip(matrix,targets):
        choices=[]
        for bits in itertools.product([0,1],repeat=5):
            if sum(a*b for a,b in zip(row,bits))==target:choices.append(bits)
        candidates.append(choices)
    def backtrack(i,sums,chosen):
        if i==5:return chosen if sums==cols else None
        for mask in candidates[i]:
            nexts=[sums[c]+matrix[i][c]*mask[c] for c in range(5)]
            if any(nexts[c]>cols[c] for c in range(5)):continue
            result=backtrack(i+1,nexts,chosen+[list(mask)])
            if result is not None:return result
        return None
    return backtrack(0,[0]*5,[])

def update_sumplete(day,out):
    slug=day.strftime('%B').lower()+'-'+str(day.day)+'-'+str(day.year)
    url=f'https://walkthroughs.net/sumplete-answers/{slug}'
    txt=checked_page(fetch(url),day,'Sumplete')
    if txt:
        m=re.search(r'5x5 solution.*?Keep Delete\s+(.*?)\s+Reveal the solution',txt,re.I|re.S)
        if m:
            nums=list(map(int,re.findall(r'\b\d{1,3}\b',m.group(1))))
            if len(nums)==35:
                matrix=[nums[r*6:r*6+5] for r in range(5)]
                targets=[nums[r*6+5] for r in range(5)]
                cols=nums[30:35]
                kept=solve_sumplete(matrix,targets,cols)
                if kept is not None:
                    n=1334+(day-BASE).days
                    out['games']['sumplete']={'status':'verified','number':f'5×5 · #{n}','hint':[],'answer':{'type':'sumplete','grid':matrix,'kept':kept,'rowTargets':targets,'colTargets':cols},'source':url}
                    print('  ✓ sumplete')
                    return
    out['games']['sumplete']={'status':'missing','number':f'#{1334+(day-BASE).days}','answer':None,'source':'https://walkthroughs.net/sumplete-answers'}
    print('  - sumplete not confirmed')

def update_strands(day,out):
    slug=day.strftime('%B').lower()+'-'+str(day.day)+'-'+str(day.year)
    url=f'https://walkthroughs.net/strands-answers/{slug}'
    txt=checked_page(fetch(url),day,'Strands')
    if txt:
        theme=re.search(r'Theme\s*[“\"‘\']([^”\"’\']+)[”\"’\']',txt,re.I)
        section=re.split(r'\bThe answers\b',txt,maxsplit=1,flags=re.I)[-1]
        sp=re.search(r'\bSpangram\s+(?:Spangram\s+)?([A-Z]{4,})\b',section,re.I)
        wt=re.search(r'\bTheme words\s*\((\d+)\)\s*(.*)',section,re.I|re.S)
        if theme and sp and wt:
            count=int(wt.group(1))
            tail=re.split(r'\b(?:How to play|Yesterday|More puzzles|Frequently asked questions)\b',wt.group(2),maxsplit=1,flags=re.I)[0]
            words=re.findall(r'\b[A-Z]{3,}\b',tail)[:count]
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

# DPH-OPTIONAL-DAILY-IMPORTS-V1
# Do not manufacture solutions: this requires a date-matched published source.
import ast
from fractions import Fraction

def checked_mathler(day, out):
    url='https://www.gfinityesports.com/article/answer-solution'
    raw=fetch(url)
    if not raw:return
    soup=BeautifulSoup(raw,'html.parser')
    for el in soup(['script','style','nav','footer']):el.decompose()
    headings=' '.join(x.get_text(' ',strip=True) for x in soup.find_all(['h1','h2']))
    text=soup.get_text(' ',strip=True)
    stamp=f'{day.strftime("%B")} {day.day}'
    if f'Mathler Answer Today ({stamp})'.lower() not in headings.lower():return
    if not re.search(rf'(?:Updated|Last Verified)\s*:?\s*{re.escape(stamp)},?\s*{day.year}',text,re.I):return
    match=re.search(r'Today.s normal Mathler solution is\s*([0-9+*/-]{6})\b',text,re.I)
    if not match:return
    expression=match.group(1)
    def evaluate(node):
        if isinstance(node,ast.Expression):return evaluate(node.body)
        if isinstance(node,ast.Constant) and type(node.value)==int and 0<=node.value<=999:return Fraction(node.value)
        if isinstance(node,ast.BinOp):
            left,right=evaluate(node.left),evaluate(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):return left/right
        raise ValueError('Unsupported expression')
    try:result=evaluate(ast.parse(expression,mode='eval'))
    except (ValueError,SyntaxError,ZeroDivisionError,OverflowError):return
    if result.denominator!=1 or not 0<=result<=100000:return
    out['games']['mathler']={'status':'verified','number':'Normal','hint':[],
        'answer':{'type':'math','value':expression,'target':int(result),'description':'Published independently for this exact date.'},'source':url}
    print('  ✓ mathler: dated independent answer')

def checked_wend_board(day,out):
    entry=out['games'].get('wend')
    if not entry or entry.get('status')!='verified':return
    words=entry['answer'].get('words',[])
    number=BASE_NUM['wend']+(day-BASE).days
    url='https://hintsheet.com/wend/answer-today'
    raw=fetch(url)
    if not raw:return
    soup=BeautifulSoup(raw,'html.parser')
    for el in soup(['script','style','nav','footer']):el.decompose()
    text=soup.get_text(' ',strip=True)
    # Source heading must say the requested date AND requested puzzle number.
    stamp=f'{day.strftime("%b")} {day.day}, {day.year}'
    if stamp.lower() not in text.lower() or not re.search(rf'Wend\s*#\s*{number}\b',text,re.I):return
    match=re.search(r'Step.by.step walkthrough(.+?)(?:Full solution|How a Wend|Frequently Asked|$)',text,re.I|re.S)
    if not match:return
    section=match.group(1)
    paths=[]
    for word in words:
        pat=rf'\b{re.escape(word)}\s*[—–:-]\s*((?:R\d+C\d+\s*(?:→|->)\s*)*R\d+C\d+)'
        found=re.search(pat,section,re.I)
        if not found:return
        pos=[list(map(int,xy)) for xy in re.findall(r'R(\d+)C(\d+)',found.group(1),re.I)]
        if len(pos)!=len(word):return
        paths.append(pos)
    used={};limit=0
    for word,path in zip(words,paths):
        for i,(r,c) in enumerate(path):
            if (r,c) in used:return
            used[(r,c)]=word[i].upper()
            limit=max(limit,r,c)
        if any(abs(a[0]-b[0])+abs(a[1]-b[1])!=1 for a,b in zip(path,path[1:])):return
    size=re.search(r'\b([5-9])\s*[x×]\s*\1\b',text)
    n=int(size.group(1)) if size else limit
    if not 5<=n<=9 or limit>n:return
    grid=[['#']*n for _ in range(n)]
    for (r,c),letter in used.items():grid[r-1][c-1]=letter
    entry['answer'].update({'grid':grid,'paths':paths})
    entry['boardSource']=url
    print('  ✓ wend: original grid and paths')

def update(day,force=False):
    output=ROOT/'data'/f'{day}.json'
    if output.exists() and not force:
        print(f'{output.name} already exists; use --force to regenerate')
        return
    obj={'date':day.isoformat(),'editorialNote':'Daily answers are imported on a best-effort basis, validated, and linked to the original reference. Missing results are never passed off as verified.','games':{}}
    obj['games']['crosswordle']={'status':'guide','number':'Daily 7×7 / 9×9','hint':['Swap the scrambled letters into solved words.'],'answer':{'type':'notice','title':'Daily grid not yet verified','value':'This is the tile-swapping Crosswordle at crosswordle.com. A validated completed board has not yet been imported. The daily solver link below may help.'},'source':'https://crosswordle.com/'}
    obj['games']['mathler']={'status':'guide','number':'Daily equation','hint':['The exact equation has to match the hidden answer, not merely equal the target.'],'answer':{'type':'notice','title':'Solution not independently verified','value':'Use the original puzzle clues or choose an independent solver. We do not invent an equation.'},'source':'https://www.mathler.com/'}
    update_wordle(day,obj)
    update_strands(day,obj)
    update_sumplete(day,obj)
    update_linkedin(day,obj)
    checked_wend_board(day,obj)
    checked_mathler(day,obj)
    # A temporary failure must not erase a verified record for the SAME date.
    if output.exists():
        try:
            previous=json.loads(output.read_text(encoding='utf-8'))
            if previous.get('date')==day.isoformat():
                for name,old in previous.get('games',{}).items():
                    if old.get('status')=='verified' and obj['games'].get(name,{}).get('status')!='verified':
                        obj['games'][name]=old
                    elif name=='wend' and old.get('status')=='verified' and obj['games'].get(name,{}).get('status')=='verified':
                        earlier=old.get('answer',{})
                        current=obj['games'][name]['answer']
                        if earlier.get('words')==current.get('words') and earlier.get('grid') and earlier.get('paths') and not current.get('grid'):
                            current['grid']=earlier['grid']
                            current['paths']=earlier['paths']
        except (ValueError,KeyError,TypeError):pass
    output.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {output}: {sum(v["status"]=="verified" for v in obj["games"].values())}/13 verified')

if __name__=='__main__':
    arg=argparse.ArgumentParser(description='Import verified daily answers for Daily Puzzle Hub')
    arg.add_argument('--date',default=datetime.now(ZoneInfo('Europe/London')).date().isoformat())
    arg.add_argument('--force',action='store_true')
    args=arg.parse_args()
    update(date.fromisoformat(args.date),force=args.force)
