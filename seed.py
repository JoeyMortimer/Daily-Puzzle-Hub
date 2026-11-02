import json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
steps=[('D',3),('R',1),('U',3),('R',3),('U',3),('L',5),('D',1),('R',4),('D',1),('L',4),('D',5),('R',3),('U',2),('R',1),('D',2),('R',3),('U',7),('L',1),('D',6),('L',1),('U',2),('L',2)]
r,c=4,2
path=[[r,c]]
for d,n in steps:
    dr,dc={'D':(1,0),'R':(0,1),'U':(-1,0),'L':(0,-1)}[d]
    for _ in range(n):
        r+=dr;c+=dc;path.append([r,c])
assert len(path)==len({tuple(p) for p in path})==64 and all(1<=r<=8 and 1<=c<=8 for r,c in path)
patches=[[1,1,4,1],[1,2,4,2],[1,3,3,4],[1,5,1,8],[2,5,2,7],[2,8,8,8],[3,5,3,7],[4,3,5,5],[4,6,5,7],[5,1,6,2],[6,3,6,7],[7,1,8,1],[7,2,8,4],[7,5,8,7]]
occupied=[]
for a,b,x,y in patches:
    occupied += [(r,c) for r in range(a,x+1) for c in range(b,y+1)]
assert len(occupied)==len(set(occupied))==64
sudoku=[[6,5,2,1,3,4],[3,1,4,6,2,5],[1,4,3,5,6,2],[2,6,5,4,1,3],[5,2,1,3,4,6],[4,3,6,2,5,1]]
assert all(set(row)==set(range(1,7)) for row in sudoku)
tango=['M M S S M S','M S M S S M','S M S M M S','M S M S S M','S S M M S M','S M S M M S']
assert all(row.split().count('M')==3 for row in tango)
answer={
    'date':'2026-11-01', 'editorialNote':'Solutions recorded for 1 November 2026. Other dates only appear when their own data has been supplied.',
    'games':{
      'wordle':{'status':'verified','number':'#1961','hint':['Five letters.','Two vowels, no repeated letters.','Starts with V and ends with R.'], 'answer':{'type':'word','value':'VIPER'},'source':'https://www.today-wordle.com/'},
      'strands':{'status':'verified','number':'#973','hint':['Theme: “For the rest of the day”.','Seven theme words, one eight-letter spangram.','Think sleep and taking a break.'],'answer':{'type':'strands','theme':'For the rest of the day','spangram':'ZZZZZZZZ','words':['CATNAP','DOZE','DROWSE','SIESTA','SLEEP','SLUMBER','SNOOZE']},'source':'https://hintsheet.com/strands/answer-today'},
      'crosswordle':{'status':'guide','number':'Original game','hint':['This version works backwards: you see the target word and coloured tiles.','More than one set of valid guess words may solve a board.'],'answer':{'type':'notice','title':'No single fixed answer','value':'The original reverse-Wordle Crosswordle accepts multiple valid rows. Open the game for the coloured pattern; a unique daily word list is not available here.'},'source':'https://allthedles.com/games/crosswordle/'},
      'mathler':{'status':'example','number':'Normal · target 2','hint':['The screenshot you shared has target 2.','Your green clues fix ÷6 at the end.','An expression matching the visible clues: 8−36÷6.'],'answer':{'type':'math','value':'8−36÷6','description':'This is a valid calculation matching the screenshot clues, not a verified official hidden equation.'},'source':'https://www.mathler.com/'},
      'sumplete':{'status':'verified','number':'5×5 · #1334','hint':['The first row keeps 5 and 7.','The fourth row removes everything.','The second column keeps nothing.'],'answer':{'type':'sumplete','grid':[[5,2,7,3,9],[7,5,9,8,1],[8,8,4,5,6],[7,3,6,4,7],[5,6,6,9,4]],'kept':[[1,0,1,0,0],[0,0,1,1,0],[1,0,1,1,1],[0,0,0,0,0],[1,0,0,0,0]],'rowTargets':[12,17,23,0,5],'colTargets':[18,0,20,13,6]},'source':'https://walkthroughs.net/sumplete-answers/november-1-2026'},
      'pinpoint':{'status':'verified','number':'#915','hint':['Clues: Hard, Digital, Advance.','Two further clues: Backup, Carbon (the second C of CC).'],'answer':{'type':'word','value':'Words that come before “copy”'},'source':'https://awa.games/linkedin-games/'},
      'crossclimb':{'status':'verified','number':'#915','hint':['A four-letter word ladder.','The two outer answers describe what some people do at the end of daylight saving time.'],'answer':{'type':'ladder','words':['FALL','CALL','CULL','BULL','BULK','BUCK','BACK'],'description':'Bookend phrase: FALL BACK. Middle words form the one-letter-change ladder.'},'source':'https://www.thewordfinder.com/linkedin-games-hub/crossclimb-hints/'},
      'queens':{'status':'verified','number':'#915','hint':['Nine queens on a 9×9 board.','Rows 2 and 3 use columns 2 and 5.','Last three rows use columns 8, 6 and 3.'],'answer':{'type':'queens','cols':[9,2,5,7,1,4,8,6,3]},'source':'https://lianswers.com/linkedin/queens/915-answer/'},
      'tango':{'status':'verified','number':'#755','hint':['Six-by-six board, three suns and three moons per row.','Row 1 begins moon, moon, sun.','Use the = and × constraints in the original game.'],'answer':{'type':'tango','rows':[s.split() for s in tango]},'source':'https://lianswers.com/linkedin/tango/755-answer/'},
      'zip':{'status':'verified','number':'#594','hint':['The path uses every cell in an 8×8 board.','Start at R4C2 and travel down three cells.','The route finishes at R5C4.'],'answer':{'type':'zip','path':path},'source':'https://gridpuzzles.app/zip/answers/2026-11-01/'},
      'mini-sudoku':{'status':'verified','number':'#447','hint':['Six-by-six Sudoku with 2×3 regions.','Each row has digits 1–6 exactly once.'],'answer':{'type':'sudoku','rows':sudoku},'source':'https://lianswers.com/linkedin/mini-sudoku/447-answer/'},
      'patches':{'status':'verified','number':'#229','hint':['Fourteen rectangular patches cover the 8×8 grid.','Two 4-cell vertical strips occupy columns 1 and 2 at the top.','Row 6 has a five-cell horizontal strip.'],'answer':{'type':'patches','rects':patches},'source':'https://lianswers.com/linkedin/patches/229-answer/'},
      'wend':{'status':'verified','number':'#146','hint':['Six words with lengths 5 through 10.','One is a volcano-related phenomenon.','The shortest word is NOVEL.'],'answer':{'type':'words','words':['NOVEL','VISION','VOLCANO','TURNOVER','SUPERNOVA','INNOVATION']},'source':'https://lianswers.com/linkedin/wend/146-answer/'},
    }
}
for i,row in enumerate(answer['games']['sumplete']['answer']['grid']):
 keep=answer['games']['sumplete']['answer']['kept'][i]
 assert sum(n*x for n,x in zip(row,keep))==answer['games']['sumplete']['answer']['rowTargets'][i]
for c in range(5):
 assert sum(answer['games']['sumplete']['answer']['grid'][r][c]*answer['games']['sumplete']['answer']['kept'][r][c] for r in range(5))==answer['games']['sumplete']['answer']['colTargets'][c]
(D/'data'/'2026-11-01.json').write_text(json.dumps(answer,ensure_ascii=False,indent=2)+'\n')
print('Created verified daily data for 13 entries.')
