#!/usr/bin/env python3
"""Import a Queens board screenshot using verified automatic crop detection.

Extracts colour regions from the actual pictured grid, checks connectivity and
a unique independent solution. Dry-run by default; saves only after review.
Requires Pillow (`python -m pip install pillow`).
"""
import argparse
from collections import deque
from datetime import date
import json
from pathlib import Path
import statistics
import sys

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit('Pillow missing: python -m pip install pillow') from exc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
try:
    from queens_solver import solve
except ImportError as exc:
    raise SystemExit('Cannot find scripts/queens_solver.py. Install the Queens solver first.') from exc


def dist2(a, b):
    return sum((x-y)**2 for x, y in zip(a, b))


def colour_samples(im, n):
    w, h = im.size
    if min(w, h) < n*18 or abs(w-h) > max(w, h)*0.065:
        raise ValueError(f'Board crop is {w}x{h}. Crop tightly around the square board, not the whole webpage.')
    # Median of many interior points ignores most icons, crowns and gridlines.
    offsets = (.17,.26,.35,.65,.74,.83)
    cells=[]
    for r in range(n):
        for c in range(n):
            pixels=[im.getpixel((min(w-1,int((c+x)*w/n)), min(h-1,int((r+y)*h/n))))
                    for x in offsets for y in offsets]
            cells.append(tuple(int(statistics.median(p[k] for p in pixels)) for k in range(3)))
    return cells


def group_colours(samples, n):
    # Farthest-first initialization, followed by deterministic k-means.
    # Uniform cell backgrounds are used, not arbitrary screenshot pixels.
    centers=[tuple(map(float,samples[0]))]
    for _ in range(1,n):
        candidate=max(samples,key=lambda p:min(dist2(p,c) for c in centers))
        if min(dist2(candidate,c) for c in centers)<100:
            raise ValueError('Fewer than expected visibly distinct region colours.')
        centers.append(tuple(map(float,candidate)))
    assignments=[]
    for _ in range(60):
        groups=[[] for _ in range(n)]
        fresh=[]
        for p in samples:
            ix=min(range(n),key=lambda k:dist2(p,centers[k]))
            fresh.append(ix)
            groups[ix].append(p)
        if any(not g for g in groups):
            raise ValueError('Colour clustering failed; check the crop.')
        updated=[tuple(sum(p[c] for p in g)/len(g) for c in range(3)) for g in groups]
        if fresh==assignments:
            centers=updated
            break
        assignments,centers=fresh,updated
    if len(assignments)!=n*n:
        raise ValueError('Colour grouping failed.')
    # Distinguish classes by first cell encountered, not by arbitrary cluster index.
    order=list(dict.fromkeys(assignments))
    labels={index:chr(65+k) for k,index in enumerate(order)}
    rows=[''.join(labels[assignments[r*n+c]] for c in range(n)) for r in range(n)]
    palette={labels[ix]: '#'+''.join(f'{round(v):02x}' for v in centers[ix]) for ix in order}
    return rows,palette


def check_regions(rows):
    n=len(rows)
    seen=set()
    for symbol in set(''.join(rows)):
        start=next((r,c) for r in range(n) for c in range(n) if rows[r][c]==symbol)
        seen={start}
        todo=deque([start])
        while todo:
            r,c=todo.popleft()
            for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0<=rr<n and 0<=cc<n and rows[rr][cc]==symbol and (rr,cc) not in seen:
                    seen.add((rr,cc)); todo.append((rr,cc))
        total=sum(x==symbol for row in rows for x in row)
        if len(seen)!=total:
            raise ValueError(f'Region {symbol} is not connected. Adjust crop or inspect the original board.')




def long_segments(image, direction, minimum):
    """Find sustained dark horizontal/vertical strokes (especially outer borders).

    Only a very small number of lines should qualify, even if the screenshot
    includes labels or instructions away from the puzzle.
    """
    pix=image.load()
    width,height=image.size
    outer=height if direction=='h' else width
    inner=width if direction=='h' else height
    found=[]
    for line in range(outer):
        begin=None
        for pos in range(inner+1):
            if pos < inner:
                rgb=pix[pos,line] if direction=='h' else pix[line,pos]
                dark=max(rgb)<130
            else:
                dark=False
            if dark and begin is None:
                begin=pos
            elif not dark and begin is not None:
                if pos-begin >= minimum:
                    found.append((line,begin,pos-1))
                begin=None
    return found


def detect_candidates(image,n):
    """Infer grid crop from matching horizontal border runs and vertical support.

    Unlike centring a square, this looks for the real outline. Supports uneven
    margins and taller or wider page screenshots. The solver verifies candidates.
    """
    width,height=image.size
    minimum=max(n*14,round(min(width,height)*0.12))
    horizontal=long_segments(image,'h',minimum)
    vertical=long_segments(image,'v',minimum)
    if not horizontal:
        raise ValueError('No continuous grid border found. Try a tighter board screenshot or --crop.')
    # Large (or downscaled) screenshots are still searched using the physical
    # outline instead of assuming that the grid takes the full image height.
    possibilities={}
    for i,(top,x1a,x2a) in enumerate(horizontal):
        for bottom,x1b,x2b in horizontal[i+1:]:
            if bottom-top < n*18:
                continue
            a=x2a-x1a+1
            b=x2b-x1b+1
            side=bottom-top+1
            if abs(a-side)>side*.09 or abs(b-side)>side*.09:
                continue
            allowance=max(9,round(side*.05))
            if abs(x1a-x1b)>allowance or abs(x2a-x2b)>allowance:
                continue
            left=round((x1a+x1b)/2)
            right=round((x2a+x2b)/2)
            # Find supporting vertical strokes near both horizontal endpoints.
            matching_left=[(x,yl,yh) for x,yl,yh in vertical
                           if abs(x-left)<=allowance and yl<=top+allowance and yh>=bottom-allowance]
            matching_right=[(x,yl,yh) for x,yl,yh in vertical
                            if abs(x-right)<=allowance and yl<=top+allowance and yh>=bottom-allowance]
            if not (matching_left and matching_right):
                continue
            # Outer corners of the detected vertical strokes form the true box.
            vl=min(x for x,_,_ in matching_left)
            vr=max(x for x,_,_ in matching_right)
            vt=min(top,min(y for _,y,_ in matching_left+matching_right))
            vb=max(bottom,max(y for _,_,y in matching_left+matching_right))
            if min(vr-vl+1,vb-vt+1)<n*18:
                continue
            if abs((vr-vl)-(vb-vt))>max(12,(vb-vt)*.06):
                continue
            rect=(max(0,vl),max(0,vt),min(width,vr+1),min(height,vb+1))
            score=(side, (vr-vl)+(vb-vt))
            if rect not in possibilities or score>possibilities[rect]:
                possibilities[rect]=score
    return sorted(possibilities, key=lambda rect:possibilities[rect],reverse=True)


def interpret_crop(image,n):
    rows,palette=group_colours(colour_samples(image,n),n)
    check_regions(rows)
    solutions=solve(rows)
    if len(solutions)!=1:
        raise ValueError(f'Expected a unique Queens solution; found {len(solutions)} (at most 2 checked).')
    return rows,palette,solutions[0]


def identify_board(image,n, crop=None):
    if crop is not None:
        rect=crop
        return rect,*interpret_crop(image.crop(rect),n)
    rects=detect_candidates(image,n)
    valid=[]
    for rect in rects:
        try:
            rows,palette,cols=interpret_crop(image.crop(rect),n)
        except ValueError:
            continue
        valid.append((rect,rows,palette,cols))
    if not valid:
        raise ValueError(
            f'Could not identify a valid {n}×{n} Queens grid in the screenshot. '
            'Check that the full rectangular border is visible; otherwise use --crop.'
        )
    # Multiple pixel-close outlines are fine if their region assignments agree.
    layouts={tuple(item[1]) for item in valid}
    if len(layouts)!=1:
        raise ValueError('Multiple different valid boards found; use --crop to select the intended board.')
    # The largest valid outline wins if pixel-close variants have the same layout.
    return valid[0]


def preflight_identity(args,cols):
    boards_path=ROOT/'data'/'queens_boards.json'
    if boards_path.exists():
        boards=json.loads(boards_path.read_text(encoding='utf8'))
        old=boards.get(args.date)
        if old:
            if old.get('number')!=args.number:
                raise ValueError(f'Saved board for {args.date} is #{old.get("number")}, not #{args.number}.')
            old_cols=solve(old['regions'])
            if len(old_cols)==1 and old_cols[0]!=cols:
                raise ValueError(f'Screenshot solves to {cols} but saved dated board solves to {old_cols[0]}.')
    daily_path=ROOT/'data'/f'{args.date}.json'
    if daily_path.exists():
        daily=json.loads(daily_path.read_text(encoding='utf8'))
        game=daily.get('games',{}).get('queens') or {}
        game_number=str(game.get('number') or '').lstrip('#')
        if game_number and game_number!=str(args.number):
            raise ValueError(f'Saved daily answer is #{game_number}, not #{args.number}.')
        previous_cols=(game.get('answer') or {}).get('cols')
        if previous_cols and previous_cols!=cols:
            raise ValueError(f'Screenshot solves to {cols} but saved daily answer has {previous_cols}.')


def proposed_data(args,rows,palette,cols):
    """Preflight full data changes before touching any existing file."""
    boards_path=ROOT/'data'/'queens_boards.json'
    if not boards_path.exists():
        raise ValueError('Missing data/queens_boards.json. Install the Queens solver first.')
    boards=json.loads(boards_path.read_text(encoding='utf8'))
    candidate={'number':args.number,'regions':rows,'palette':palette,'source':args.source}
    previous=boards.get(args.date)
    if previous is not None and previous!=candidate and not args.replace:
        raise ValueError('A board already exists for this date. Review the preview, then use --replace.')
    if previous and previous.get('number')!=args.number:
        raise ValueError('Existing board has a different puzzle number; refusing to replace it.')
    daily_path=ROOT/'data'/f'{args.date}.json'
    daily=None
    if daily_path.exists():
        daily=json.loads(daily_path.read_text(encoding='utf8'))
        existing=daily.get('games',{}).get('queens',{})
        number=str(existing.get('number') or '').lstrip('#')
        if number and number!=str(args.number):
            raise ValueError(f'Daily data says Queens #{number}, not #{args.number}. Refusing to save.')
        old_answer=existing.get('answer') or {}
        old_cols=old_answer.get('cols')
        if old_cols and old_cols!=cols:
            raise ValueError(
                f'Existing Queens answer {old_cols} differs from screenshot solution {cols}. '
                'Refusing to overwrite verified or unverified puzzle answers.'
            )
        existing['status']='verified'
        existing['number']=f'#{args.number}'
        existing['source']=args.source
        existing['answer']={**old_answer,'type':'queens', 'cols':cols,
                            'regions':[[palette[letter] for letter in row] for row in rows]}
        daily.setdefault('games',{})['queens']=existing
    boards[args.date]=candidate
    return boards_path,boards,daily_path,daily


def safe_write(path,value):
    from tempfile import NamedTemporaryFile
    import os
    content=json.dumps(value,indent=2,ensure_ascii=False)+'\n'
    path.parent.mkdir(parents=True,exist_ok=True)
    with NamedTemporaryFile('w',dir=path.parent,encoding='utf8',delete=False) as f:
        f.write(content)
        target=Path(f.name)
    try:
        os.replace(target,path)
    finally:
        target.unlink(missing_ok=True)

def preview(rows,palette,cols,path):
    from PIL import ImageFont
    n=len(rows); size=72
    im=Image.new('RGB',(n*size,n*size),'white')
    draw=ImageDraw.Draw(im)
    for r in range(n):
        for c in range(n):
            x,y=c*size,r*size
            zone=rows[r][c]
            draw.rectangle((x,y,x+size,y+size),fill=palette[zone])
            if r==0 or rows[r-1][c]!=zone: draw.line((x,y,x+size,y),fill='#222222',width=3)
            if c==0 or rows[r][c-1]!=zone: draw.line((x,y,x,y+size),fill='#222222',width=3)
            if r==n-1 or rows[r+1][c]!=zone: draw.line((x,y+size-2,x+size,y+size-2),fill='#222222',width=3)
            if c==n-1 or rows[r][c+1]!=zone: draw.line((x+size-2,y,x+size-2,y+size),fill='#222222',width=3)
            if cols[r]==c+1:
                draw.ellipse((x+18,y+18,x+size-18,y+size-18), fill='#203c35')
                draw.text((x+size/2,y+size/2),'Q',anchor='mm',fill='white')
    im.save(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path,help='Screenshot including the Queens coloured board')
    parser.add_argument('--date',help='YYYY-MM-DD for the original LinkedIn puzzle')
    parser.add_argument('--number',type=int,help='Verified LinkedIn Queens puzzle number')
    parser.add_argument('--size',type=int,default=7,help='Board dimension (default: 7)')
    parser.add_argument('--inspect',action='store_true',help='Inspect an unknown screenshot without date/number and without saving')
    parser.add_argument('--crop',help='Override auto-detection: x1,y1,x2,y2')
    parser.add_argument('--expect',help='Optional known queen columns, e.g. 7,2,4,6,3,5,1')
    parser.add_argument('--source',default='manual screenshot (source not recorded)')
    parser.add_argument('--preview',type=Path,default=Path('queens-preview.png'))
    parser.add_argument('--save',action='store_true',help='After reviewing preview, save to the daily data files')
    parser.add_argument('--replace',action='store_true',help='Replace a matching-number, dated region map after review')
    args=parser.parse_args()
    if args.inspect:
        if args.save or args.replace or args.date or args.number is not None:
            parser.error('--inspect is for undated previews only; omit --date, --number, --save and --replace')
    else:
        if not args.date or args.number is None:
            parser.error('--date and --number are required to label or save a daily puzzle; use --inspect for a test')
        date.fromisoformat(args.date)
        if args.number<=0:
            parser.error('--number must be the real LinkedIn puzzle number, not a placeholder')
    if not 5<=args.size<=12:
        parser.error('--size must be between 5 and 12')
    expected=None
    if args.expect:
        try: expected=[int(x) for x in args.expect.split(',')]
        except ValueError: parser.error('--expect must be comma-separated integers')
        if len(expected)!=args.size or any(not 1<=c<=args.size for c in expected):
            parser.error('--expect must contain one column 1..size for each row')
    image=Image.open(args.image).convert('RGB')
    crop=None
    if args.crop:
        try: crop=tuple(int(k) for k in args.crop.split(','))
        except ValueError: parser.error('--crop must be x1,y1,x2,y2')
        if len(crop)!=4 or crop[0]<0 or crop[1]<0 or crop[2]>image.width or crop[3]>image.height or crop[0]>=crop[2] or crop[1]>=crop[3]:
            parser.error('--crop coordinates invalid or outside image')
    rect,rows,palette,cols=identify_board(image,args.size,crop)
    if expected is not None and cols!=expected:
        raise SystemExit(f'Rejected: solver {cols} does NOT match expected {expected}.')
    # Do not even label a screenshot as this date/puzzle if it conflicts with
    # an already known answer. Checks apply in DRY RUN as well as save mode.
    if not args.inspect:
        try:
            preflight_identity(args,cols)
        except ValueError as exc:
            raise SystemExit('REJECTED: '+str(exc))
        print(f'Queens #{args.number} — {args.date}')
    else:
        print('Queens screenshot inspection — date and puzzle number unverified')
    print('Detected crop:', ','.join(str(x) for x in rect))
    print('\n'.join(rows))
    print('Unique solution:',cols)
    preview(rows,palette,cols,args.preview)
    print('Preview saved:',args.preview)
    if not args.save:
        print('DRY RUN: No data changed. Verify the preview, date and puzzle number before --save.')
        return
    try:
        boards_path,boards,daily_path,daily=proposed_data(args,rows,palette,cols)
    except ValueError as exc:
        raise SystemExit('REJECTED: '+str(exc))
    safe_write(boards_path,boards)
    print('Saved:',boards_path)
    if daily is not None:
        safe_write(daily_path,daily)
        print('Updated:',daily_path)
        print('NEXT: python scripts/validate.py && python scripts/embed.py')
    else:
        print('No dated daily file yet; the scheduled updater will use this saved board.')

if __name__=='__main__':
    main()
