"""Daily Puzzle Hub: independent Tango and 6x6 Mini Sudoku solvers.

No network access. Never invent starting boards, dates or puzzle numbers.
Tango rules: balanced rows/columns, no triples, optional same/opposite links.
Mini Sudoku rules: rows/columns and 2x3 boxes contain 1..6 once each.
"""
from __future__ import annotations

from datetime import date
from itertools import product
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIGITS = frozenset(range(1, 7))


class PuzzleError(ValueError):
    """Bad source board, ambiguous solution or disagreement with saved data."""


def _board6(rows, label):
    if not isinstance(rows, list) or len(rows) != 6 or any(
        not isinstance(row, list) or len(row) != 6 for row in rows
    ):
        raise PuzzleError(f"{label}: expected a 6x6 list of rows")


def _tango_inputs(givens, links):
    _board6(givens, "Tango givens")
    norm = []
    for r, row in enumerate(givens, 1):
        new = []
        for c, v in enumerate(row, 1):
            sym = str(v).strip().upper() if v is not None else '.'
            if sym in ('.', '', '0', '-', '?'):
                new.append('.')
            elif sym in ('S', 'SUN', '☀', '☀️'):
                new.append('S')
            elif sym in ('M', 'MOON', '☾', '🌙'):
                new.append('M')
            else:
                raise PuzzleError(f"Tango R{r}C{c}: use S, M or .")
        norm.append(new)
    if not isinstance(links, list):
        raise PuzzleError("Tango links must be a list")
    relations = {}
    normalized = []
    for i, link in enumerate(links, 1):
        if not isinstance(link, dict):
            raise PuzzleError(f"Tango link {i}: expected an object")
        a = link.get('a', link.get('from'))
        b = link.get('b', link.get('to'))
        rel = str(link.get('relation', link.get('rel', ''))).strip().lower()
        if rel in ('=', 'same', 'equal'):
            rel = '='
        elif rel in ('x', '×', 'different', 'opposite', '!='):
            rel = 'x'
        else:
            raise PuzzleError(f"Tango link {i}: relation must be = or x")
        for coord in (a, b):
            if (not isinstance(coord, (list, tuple)) or len(coord) != 2
                or any(type(x) is not int or not 1 <= x <= 6 for x in coord)):
                raise PuzzleError(f"Tango link {i}: coordinates must be [row,column], 1..6")
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            raise PuzzleError(f"Tango link {i}: endpoints must be neighbouring cells")
        key = tuple(sorted(((a[0] - 1, a[1] - 1), (b[0] - 1, b[1] - 1))))
        if key in relations and relations[key] != rel:
            raise PuzzleError(f"Tango link {i}: contradictory constraints")
        if key not in relations:
            relations[key] = rel
            normalized.append({'a': list(a), 'b': list(b), 'relation': rel})
    return norm, relations, normalized


def solve_tango(givens, links=None, limit=2):
    """Return at most `limit` solutions as 6x6 S/M grids."""
    if type(limit) is not int or limit < 1:
        raise PuzzleError("limit must be positive")
    given, relations, _ = _tango_inputs(givens, links if links is not None else [])
    all_rows = [row for row in product('SM', repeat=6)
                if row.count('S') == 3 and all(not (row[i] == row[i+1] == row[i+2]) for i in range(4))]
    candidates = []
    for r in range(6):
        found = []
        for row in all_rows:
            if any(given[r][c] != '.' and row[c] != given[r][c] for c in range(6)):
                continue
            if any(((row[c1] == row[c2]) != (rel == '='))
                   for ((r1, c1), (r2, c2)), rel in relations.items()
                   if r1 == r2 == r):
                continue
            found.append(row)
        candidates.append(found)
    solutions = []
    chosen = []
    suns = [0] * 6

    def visit(r):
        if len(solutions) >= limit:
            return
        if r == 6:
            if all(v == 3 for v in suns):
                solutions.append([list(row) for row in chosen])
            return
        for row in candidates[r]:
            if any(suns[c] + (row[c] == 'S') > 3 or
                   suns[c] + (row[c] == 'S') + (5-r) < 3 for c in range(6)):
                continue
            if r >= 2 and any(chosen[r-2][c] == chosen[r-1][c] == row[c] for c in range(6)):
                continue
            if r >= 1:
                ok = True
                for ((r1, c1), (r2, c2)), rel in relations.items():
                    if r1 == r-1 and r2 == r:
                        if (chosen[r-1][c1] == row[c2]) != (rel == '='):
                            ok = False
                            break
                if not ok:
                    continue
            chosen.append(row)
            for c in range(6):
                suns[c] += (row[c] == 'S')
            visit(r+1)
            for c in range(6):
                suns[c] -= (row[c] == 'S')
            chosen.pop()
            if len(solutions) >= limit:
                return
    visit(0)
    return solutions


def _sudoku_inputs(givens):
    _board6(givens, "Mini Sudoku givens")
    out = []
    for r, row in enumerate(givens, 1):
        new = []
        for c, v in enumerate(row, 1):
            if v is None or v == '.' or v == '':
                new.append(0)
            elif type(v) is int and 0 <= v <= 6:
                new.append(v)
            elif isinstance(v, str) and v in '0123456' and len(v) == 1:
                new.append(int(v))
            else:
                raise PuzzleError(f"Mini Sudoku R{r}C{c}: expected 0..6")
        out.append(new)
    return out


def solve_sudoku(givens, limit=2):
    """Solve 6x6 Sudoku with 2-row x 3-column boxes; stop after limit."""
    if type(limit) is not int or limit < 1:
        raise PuzzleError("limit must be positive")
    grid = _sudoku_inputs(givens)
    rows = [set() for _ in range(6)]
    cols = [set() for _ in range(6)]
    boxes = [set() for _ in range(6)]

    def box_id(r, c):
        return (r // 2) * 2 + c // 3

    blanks = []
    for r in range(6):
        for c in range(6):
            v = grid[r][c]
            if v == 0:
                blanks.append((r, c))
            else:
                bi = box_id(r, c)
                if v in rows[r] or v in cols[c] or v in boxes[bi]:
                    raise PuzzleError(f"Mini Sudoku: conflicting given at R{r+1}C{c+1}")
                rows[r].add(v)
                cols[c].add(v)
                boxes[bi].add(v)
    answers = []

    def visit():
        if len(answers) >= limit:
            return
        if not blanks:
            answers.append([row.copy() for row in grid])
            return
        best = None
        options = DIGITS
        for r, c in blanks:
            avail = DIGITS - rows[r] - cols[c] - boxes[box_id(r, c)]
            if not avail:
                return
            if len(avail) < len(options) or best is None:
                best, options = (r, c), avail
                if len(options) == 1:
                    break
        r, c = best
        blanks.remove(best)
        bi = box_id(r, c)
        for v in sorted(options):
            grid[r][c] = v
            rows[r].add(v)
            cols[c].add(v)
            boxes[bi].add(v)
            visit()
            boxes[bi].remove(v)
            cols[c].remove(v)
            rows[r].remove(v)
            grid[r][c] = 0
            if len(answers) >= limit:
                break
        blanks.append(best)
    visit()
    return answers


def _input_for_game(game, entry):
    if not isinstance(entry, dict):
        raise PuzzleError(f"{game}: board entry must be an object")
    if 'givens' not in entry:
        raise PuzzleError(f"{game}: missing original starting grid (givens)")
    if game == 'tango':
        givens, links, normalized_links = _tango_inputs(entry['givens'], entry.get('links', []))
        solved = solve_tango(givens, normalized_links)
        return solved, {'givens': givens, 'links': normalized_links}
    if game == 'mini-sudoku':
        givens = _sudoku_inputs(entry['givens'])
        solved = solve_sudoku(givens)
        return solved, {'givens': givens}
    raise PuzzleError(f"Unsupported game: {game}")


def solve_game(game, entry):
    solved, inputs = _input_for_game(game, entry)
    if not solved:
        raise PuzzleError(f"{game}: no valid solution; inspect givens or links")
    if len(solved) != 1:
        raise PuzzleError(f"{game}: multiple solutions; more original clues are needed")
    return solved[0], inputs


def _number(value):
    if type(value) is int and value > 0:
        return value
    if isinstance(value, str) and re.fullmatch(r'#?[1-9]\d*', value):
        return int(value.lstrip('#'))
    raise PuzzleError("Each board needs its real, verified puzzle number")


def _source(entry, game):
    url = entry.get('source', f'https://www.linkedin.com/games/{game}')
    if not isinstance(url, str) or not url.startswith('https://'):
        raise PuzzleError(f"{game}: source must be an https:// URL")
    return url


def apply_to_daily(board, daily):
    """Merge independently solved boards with existing daily JSON in memory.

    Returns games updated. Rejects mismatched dates/numbers and conflicting answers.
    Board must come from a verified original daily puzzle, never from a solution grid.
    """
    if not isinstance(board, dict) or not isinstance(daily, dict):
        raise PuzzleError("Invalid board/daily JSON")
    day = board.get('date')
    try:
        date.fromisoformat(day)
    except (TypeError, ValueError):
        raise PuzzleError("Board needs a real ISO date, e.g. 2026-11-03") from None
    if daily.get('date') != day:
        raise PuzzleError(f"Date mismatch: board {day}, daily {daily.get('date')}")
    updates = {}
    games = daily.setdefault('games', {})
    for game in ('tango', 'mini-sudoku'):
        if game not in board:
            continue
        entry = board[game]
        num = _number(entry.get('number'))
        answer, inputs = solve_game(game, entry)
        existing = games.get(game) or {}
        old_num = existing.get('number')
        if old_num not in (None, '', 'Awaiting answer') and old_num != f'#{num}':
            raise PuzzleError(f"{game}: puzzle-number mismatch ({old_num} vs #{num})")
        old_answer = existing.get('answer') or {}
        if existing.get('status') == 'verified' and old_answer.get('rows') is not None:
            original = old_answer['rows']
            original = (_sudoku_inputs(original) if game == 'mini-sudoku' else
                        _tango_inputs(original, [])[0])
            if original != answer:
                raise PuzzleError(f"{game}: independent solver disagrees with published answer")
        new_answer = {**old_answer,
                      'type': 'tango' if game == 'tango' else 'sudoku',
                      'rows': answer, **inputs,
                      'verifiedBy': 'independent-logic-solver'}
        updates[game] = {**existing,
                         'status': 'verified',
                         'number': f'#{num}',
                         'answer': new_answer,
                         'source': existing.get('source') if existing.get('status') == 'verified' else _source(entry, game),
                         'hint': existing.get('hint', [])}
    games.update(updates)
    return updates


def enrich_daily(day, obj):
    """Called by updater after other sources. No input board => no-op."""
    name = day.isoformat() if hasattr(day, 'isoformat') else str(day)
    path = ROOT / 'data' / 'logic_boards' / f'{name}.json'
    if not path.exists():
        return 0
    board = json.loads(path.read_text(encoding='utf-8'))
    updates = apply_to_daily(board, obj)
    for game in updates:
        print(f'  ✓ {game}: independently solved from original givens')
    return len(updates)
