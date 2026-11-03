#!/usr/bin/env python3
"""Preview and optionally publish independently solved Tango/Mini Sudoku boards."""
import argparse
from pathlib import Path
import json
from logic_solvers import ROOT, PuzzleError, apply_to_daily, solve_game


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('board', help='JSON file with date, puzzle number and original givens')
    p.add_argument('--apply', action='store_true', help='Merge into data/YYYY-MM-DD.json')
    p.add_argument('--replace', action='store_true', help='Permit replacing a different existing unverified result')
    args = p.parse_args()
    board = json.loads(Path(args.board).read_text(encoding='utf-8'))
    for game in ('tango', 'mini-sudoku'):
        if game not in board:
            continue
        solution, _ = solve_game(game, board[game])
        print(f'{game} — unique solution, number #{board[game].get("number", "unverified")}')
        for row in solution:
            print('  ', ' '.join(map(str, row)))
    if not args.apply:
        print('DRY RUN: no files changed. Supply --apply after checking date/number and original givens.')
        return
    day = board.get('date')
    if not isinstance(day, str):
        raise PuzzleError('Missing date')
    daily_file = ROOT / 'data' / f'{day}.json'
    if daily_file.exists():
        daily = json.loads(daily_file.read_text(encoding='utf-8'))
    else:
        daily = {'date': day, 'games': {}}
    previous = json.dumps(daily, sort_keys=True)
    updates = apply_to_daily(board, daily)
    if not updates:
        raise PuzzleError('No Tango or Mini Sudoku boards supplied')
    if not args.replace:
        # Do not silently change an existing unverified solution or guide.
        for game in updates:
            before = json.loads(previous).get('games', {}).get(game) or {}
            old_rows = (before.get('answer') or {}).get('rows')
            if old_rows and before.get('status') != 'verified':
                raise PuzzleError(f'{game}: old non-verified grid exists; inspect it before --replace')
    daily_file.parent.mkdir(parents=True, exist_ok=True)
    daily_file.write_text(json.dumps(daily, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Saved {daily_file}. Now run python scripts/validate.py and python scripts/embed.py.')


if __name__ == '__main__':
    try:
        main()
    except (PuzzleError, OSError, ValueError) as e:
        raise SystemExit(f'ERROR: {e}')
