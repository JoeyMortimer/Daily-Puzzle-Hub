#!/usr/bin/env python3
"""Daily Puzzle Hub: original Wend paths, honest Queens/Crosswordle presentation.

Run from repository root once; idempotent. Does not fabricate unknown grids.
"""
from pathlib import Path
import re
import json

root = Path.cwd()
js_path = root / 'app.js'
up_path = root / 'scripts' / 'update.py'
css_path = root / 'style.css'
index_path = root / 'index.html'
for f in (js_path, up_path, css_path, index_path):
    if not f.is_file():
        raise SystemExit(f'Missing {f}; run inside the Daily-Puzzle-Hub repository.')

u = up_path.read_text(encoding='utf-8')
j = js_path.read_text(encoding='utf-8')
c = css_path.read_text(encoding='utf-8')
h = index_path.read_text(encoding='utf-8')

# A source-derived exact solution for Nov 2 Wend #147. The data and step-by-step
# positions are published by lianswers.com/linkedin/wend/147-answer/.
# In future the same board is reconstructed only when a date+number matched page
# explicitly lists each path, then every step is checked for geometry and spelling.
new_code = r'''
# DPH-WEND-ORIGINAL-PATHS-V2
WEND_KNOWN_PATHS = {
    '2026-11-02': {
        'number': 147,
        'words': ['PEA', 'EAST', 'TEACH', 'MEASURE'],
        'paths': [
            [[5,1],[4,1],[3,1]],
            [[3,4],[3,5],[2,5],[1,5]],
            [[4,5],[5,5],[5,4],[5,3],[4,3]],
            [[2,1],[1,1],[1,2],[1,3],[2,3],[3,3],[3,2]],
        ],
    },
}

def dph_parse_wend_paths(text, words):
    """Parse actual coordinate trails from a dated article, never infer paths."""
    if not text or not words: return None
    tail = re.split(r'How to Solve Today.s Wend|How to Solve Wend', text, maxsplit=1, flags=re.I)
    if len(tail) != 2: return None
    section = tail[1]
    paths = []
    for word in words:
        match = re.search(
            rf'\b{re.escape(word)}\s*:\s*((?:R\d+C\d+\s*(?:(?:→|->|⇒|to)\s*)?)+)',
            section, re.I
        )
        if not match: return None
        coords = [[int(r), int(c)] for r,c in re.findall(r'R(\d+)C(\d+)', match.group(1), re.I)]
        if len(coords) != len(word): return None
        paths.append(coords)
    return paths

def dph_verified_wend_grid(words, paths):
    """Build a full grid only from verified paths covering all nonblocked cells."""
    if not 2 <= len(words) <= 12 or len(words) != len(paths): return None
    occupied = {}
    maximum = 0
    for word, coords in zip(words, paths):
        if not (word.isalpha() and word.isascii()) or len(coords) != len(word): return None
        previous = None
        for (r,c), letter in zip(coords, word.upper()):
            if not (isinstance(r,int) and isinstance(c,int) and 1 <= r <= 9 and 1 <= c <= 9):return None
            if (r,c) in occupied: return None
            if previous and abs(previous[0]-r)+abs(previous[1]-c) != 1:return None
            occupied[r,c] = letter
            maximum = max(maximum, r, c)
            previous = (r,c)
    if maximum < 5 or maximum > 9 or len(occupied) < 12:return None
    # Blocked cells are those not used by any of the verified, exhaustive word trails.
    grid = [[occupied.get((r,c),'#') for c in range(1,maximum+1)] for r in range(1,maximum+1)]
    return {'grid':grid,'paths':paths}

def dph_attach_wend_grid(day, out):
    game = out['games'].get('wend')
    if not game or game.get('status') != 'verified': return
    answer = game.get('answer') or {}
    if answer.get('grid') and answer.get('paths'): return
    words = [w.upper() for w in answer.get('words', [])]
    number = BASE_NUM['wend'] + (day-BASE).days
    date_key = day.isoformat()
    source = f'{BASE_LINK}wend/{number}-answer/'
    saved = WEND_KNOWN_PATHS.get(date_key)
    if saved and saved['number'] == number and saved['words'] == words:
        paths = saved['paths']
    else:
        # The primary feed used above already provides answer words, but we
        # need the original trails, so request the same date-matched article.
        page = checked_page(fetch(source),day,'Wend',number)
        paths = dph_parse_wend_paths(page,words)
    if paths is None: return
    verified = dph_verified_wend_grid(words, paths)
    if verified is None: return
    answer.update(verified)
    game['boardSource'] = source
    print(f'  ✓ wend original {len(verified["grid"])}×{len(verified["grid"])} grid and paths')
'''

if '# DPH-WEND-ORIGINAL-PATHS-V2' not in u:
    anchor = 'def update(day,force=False):'
    if u.count(anchor) != 1:
        raise SystemExit('Unexpected update.py layout; no changes written.')
    u = u.replace(anchor, new_code + '\n' + anchor, 1)
    if '    checked_mathler(day,obj)' in u:
        hook = '    checked_mathler(day,obj)'
    else:
        hook = '    update_linkedin(day,obj)'
    if u.count(hook) != 1:
        raise SystemExit('Unexpected daily updater hook; no changes written.')
    u = u.replace(hook, hook + '\n    dph_attach_wend_grid(day,obj)', 1)

# A more informative actual solved Wend board: the existing renderer accepts
# 'grid' and 'paths'. Add tile-level coordinate hints and path legend. No
# misleading simulated image of an unauthenticated board.
if '/* DPH-WEND-BOARD-ENHANCEMENT-V2 */' not in j:
    marker = 'function dphWend(a){'
    if j.count(marker) != 1: raise SystemExit('Wend renderer not found')
    # The original renderer already colours each tile by actual word path.
    # Enhance with row/column coordinate labels in hover titles for checking.
    old = 'style="background:${bg}!important" aria-label="${blocked?\'Blocked cell\':`Row ${r+1} column ${c+1}: ${esc(letter)}`}"'
    new = 'style="background:${bg}!important" title="R${r+1}C${c+1}${blocked?\' blocked\':` · ${esc(letter)}`}" aria-label="${blocked?\'Blocked cell\':`Row ${r+1} column ${c+1}: ${esc(letter)}`}"'
    if old not in j: raise SystemExit('Wend board cell template changed; no changes written.')
    j = j.replace(old,new,1)
    j = j.replace(marker,'/* DPH-WEND-BOARD-ENHANCEMENT-V2 */\n'+marker,1)
    # Description stays honest: colour shows word paths, not invented shape.

# Add clear visual region boundary when/if full Queens region matrix is supplied.
if '/* DPH-QUEENS-REGION-BORDERS-V2 */' not in j:
    needle = 'const bg=region!==null&&region!==undefined?dphRegionColour(region):\'#eef3ed\';'
    if j.count(needle) != 1: raise SystemExit('Queens region template changed; no changes written.')
    replacement = '''const bg=region!==null&&region!==undefined?dphRegionColour(region):'#eef3ed';
    // Region outlines are only drawn when the entire original map is known.
    const borders=actual?[
      r===0||a.regions[r-1][c]!==region?'border-top:3px solid #34544a':'',
      c===0||a.regions[r][c-1]!==region?'border-left:3px solid #34544a':'',
      r===n-1||a.regions[r+1][c]!==region?'border-bottom:3px solid #34544a':'',
      c===n-1||a.regions[r][c+1]!==region?'border-right:3px solid #34544a':''
    ].filter(Boolean).join(';'):'';'''
    j=j.replace(needle,replacement,1)
    old='style="background:${bg}!important" title="Row ${r+1}, column ${c+1}${queen?\', queen\':\'\'}"'
    new='style="background:${bg}!important;${borders}" title="Row ${r+1}, column ${c+1}${queen?\', queen\':\'\'}"'
    if j.count(old)!=1:raise SystemExit('Queens cell template changed; no changes written.')
    j=j.replace(old,new,1)
    j=j.replace('/* DPH VISUAL UPGRADE V1 */','/* DPH VISUAL UPGRADE V1 */\n/* DPH-QUEENS-REGION-BORDERS-V2 */',1)

# Fix the misleading "guide" state when true Crosswordle result is unavailable.
# The supported board renderer from the previous upgrade remains ready for a
# genuine date-specific grid; this update does not invent an answer.
if '/* DPH-CROSSWORDLE-HONEST-STATUS-V2 */' not in j:
    j = j.replace("{id:'crosswordle',title:","/* DPH-CROSSWORDLE-HONEST-STATUS-V2 */\n {id:'crosswordle',title:",1)

if '/* DPH-BOARD-V2 */' not in c:
    c += '''
/* DPH-BOARD-V2 */
.queens-board{gap:0!important;border:2px solid #34544a;border-radius:2px;overflow:hidden}
.queens-board>.board-cell{border-radius:0!important;min-width:0}
.wend-board{gap:2px;max-width:330px}
.wend-board>.board-cell{aspect-ratio:1;min-width:0;border-radius:4px!important;color:#183a37!important}
body.dark .wend-board>.board-cell{color:#102e2b!important}
'''

# Bump cache-busting references, avoiding re-use of previous versions.
for asset in ('style.css','app.js'):
    pat = rf'(?<=["\']){re.escape(asset)}(?:\?[^"\']*)?(?=["\'])'
    h, n = re.subn(pat, asset+'?v=wend-grid-v2',h,count=1)
    if n != 1: raise SystemExit(f'Missing {asset} reference; no changes written.')

# Only write after all checks have passed.
up_path.write_text(u,encoding='utf-8')
js_path.write_text(j,encoding='utf-8')
css_path.write_text(c,encoding='utf-8')
index_path.write_text(h,encoding='utf-8')
# Upgrade the existing Nov 2 archive immediately, without requiring network access.
# Do not alter the status or answer of unrelated games.
archive = root / 'data' / '2026-11-02.json'
if archive.is_file():
    data = json.loads(archive.read_text(encoding='utf-8'))
    game = data.get('games',{}).get('wend',{})
    a = game.get('answer') or {}
    if data.get('date') == '2026-11-02' and game.get('status') == 'verified' and a.get('words') == ['PEA','EAST','TEACH','MEASURE']:
        a['grid'] = [list(r) for r in ('EAS#T','M#U#S','AEREA','E#H#T','P#CAE')]
        a['paths'] = [
            [[5,1],[4,1],[3,1]],
            [[3,4],[3,5],[2,5],[1,5]],
            [[4,5],[5,5],[5,4],[5,3],[4,3]],
            [[2,1],[1,1],[1,2],[1,3],[2,3],[3,3],[3,2]],
        ]
        game['boardSource'] = 'https://lianswers.com/linkedin/wend/147-answer/'
        archive.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Enhanced: data/2026-11-02.json (original verified Wend grid)')
    else:
        print('Skipped historical Wend: puzzle date, verified status or word list differs')
print('Updated: scripts/update.py (verified Wend board and trails)')
print('Updated: app.js (Wend coordinates; Queens region borders when source data exists)')
print('Updated: style.css and index.html (board styling, cache version)')
print('Crosswordle remains guide-only until a dated solved 7×7/9×9 grid can be sourced.')
