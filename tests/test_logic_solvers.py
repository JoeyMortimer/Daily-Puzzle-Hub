"""Offline tests: no live LinkedIn data or network needed."""
import copy
import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'scripts'))
from logic_solvers import (PuzzleError, solve_tango, solve_sudoku,
                           solve_game, apply_to_daily, enrich_daily)

SAMPLE = json.loads((BASE / 'examples' / 'logic_board_DEMO.json').read_text())


class LogicSolverTests(unittest.TestCase):
    def test_tango_unique_start(self):
        solutions = solve_tango(SAMPLE['tango']['givens'], SAMPLE['tango']['links'])
        self.assertEqual(len(solutions), 1)
        for row in solutions[0]:
            self.assertEqual(row.count('S'), 3)
            self.assertEqual(row.count('M'), 3)

    def test_tango_ambiguous_is_rejected(self):
        blank = [['.']*6 for _ in range(6)]
        self.assertEqual(len(solve_tango(blank)), 2)
        with self.assertRaisesRegex(PuzzleError, 'multiple solutions'):
            solve_game('tango', {'givens': blank, 'links': []})

    def test_tango_impossible_and_conflicting_link(self):
        board = [row[:] for row in SAMPLE['tango']['givens']]
        board[0] = ['S','S','S','.','.','.']
        self.assertEqual(solve_tango(board), [])
        with self.assertRaisesRegex(PuzzleError, 'contradictory'):
            solve_tango(SAMPLE['tango']['givens'], [
                {'a':[1,1], 'b':[1,2], 'relation': '='},
                {'a':[1,1], 'b':[1,2], 'relation': 'x'},
            ])

    def test_tango_same_and_opposite_signs(self):
        # A fully specified valid board includes both same and opposite neighbours.
        board = [list(row) for row in (
            'SSMSMM', 'SSMSMM', 'MMSMSS', 'SSMSMM', 'MMSMSS', 'MMSMSS')]
        links = [
            {'a':[1,1], 'b':[1,2], 'relation':'='},
            {'a':[1,2], 'b':[1,3], 'relation':'x'},
            {'a':[1,1], 'b':[2,1], 'relation':'same'},
            {'a':[2,1], 'b':[3,1], 'relation':'opposite'},
        ]
        self.assertEqual(solve_tango(board, links), [board])
        links[0]['relation'] = 'x'
        self.assertEqual(solve_tango(board, links), [])

    def test_tango_link_must_be_adjacent(self):
        with self.assertRaisesRegex(PuzzleError, 'neighbouring'):
            solve_tango(SAMPLE['tango']['givens'], [
                {'a': [1,1], 'b':[3,3], 'relation':'='}])

    def test_sudoku_unique_start(self):
        solutions = solve_sudoku(SAMPLE['mini-sudoku']['givens'])
        self.assertEqual(len(solutions), 1)
        self.assertEqual(solutions[0][0], [1,2,3,4,5,6])

    def test_sudoku_ambiguous_and_invalid(self):
        self.assertEqual(len(solve_sudoku([[0]*6 for _ in range(6)])), 2)
        board = copy.deepcopy(SAMPLE['mini-sudoku']['givens'])
        board[0][0] = board[0][1]
        with self.assertRaisesRegex(PuzzleError, 'conflicting given'):
            solve_sudoku(board)

    def test_no_fabricated_source_boards(self):
        for game in ('tango', 'mini-sudoku'):
            with self.assertRaisesRegex(PuzzleError, 'missing original'):
                solve_game(game, {'rows': [[1]*6 for _ in range(6)]})

    def test_merges_matching_previously_verified_answers(self):
        board = copy.deepcopy(SAMPLE)
        board['date']='2026-11-03'
        board['tango']['number'] = 757
        board['mini-sudoku']['number'] = 449
        t = solve_game('tango', board['tango'])[0]
        s = solve_game('mini-sudoku', board['mini-sudoku'])[0]
        daily = {'date':'2026-11-03', 'games': {
            'tango': {'status':'verified','number':'#757',
                      'answer':{'type':'tango','rows':t}, 'source':'https://example.org/tango'},
            'mini-sudoku': {'status':'verified','number':'#449',
                            'answer':{'type':'sudoku','rows':s}, 'source':'https://example.org/sudoku'}
        }}
        result = apply_to_daily(board,daily)
        self.assertEqual(set(result), {'tango','mini-sudoku'})
        self.assertEqual(daily['games']['tango']['answer']['links'], board['tango']['links'])
        self.assertEqual(daily['games']['mini-sudoku']['answer']['givens'], board['mini-sudoku']['givens'])
        self.assertEqual(daily['games']['tango']['source'], 'https://example.org/tango')

    def test_rejects_wrong_date_number_or_answer_and_preserves_data(self):
        board = copy.deepcopy(SAMPLE)
        board['date']='2026-11-03'
        board['tango']['number']=757
        board['mini-sudoku']['number']=449
        original = {'date':'2026-11-03','games':{
            'tango':{'status':'verified','number':'#756', 'answer':{'rows':[]}}
        }}
        daily = copy.deepcopy(original)
        with self.assertRaisesRegex(PuzzleError, 'number mismatch'):
            apply_to_daily(board, daily)
        self.assertEqual(daily, original)
        daily = {'date':'2026-11-04','games':{}}
        with self.assertRaisesRegex(PuzzleError, 'Date mismatch'):
            apply_to_daily(board, daily)
        solved = solve_game('tango', board['tango'])[0]
        changed = copy.deepcopy(solved)
        changed[0][0] = 'M' if changed[0][0] == 'S' else 'S'
        daily={'date':'2026-11-03','games':{
            'tango':{'status':'verified','number':'#757','answer':{'type':'tango','rows':changed}}
        }}
        with self.assertRaisesRegex(PuzzleError, 'disagrees'):
            apply_to_daily(board, daily)
        self.assertEqual(daily['games']['tango']['answer']['rows'], changed)

    def test_no_board_means_updater_noop(self):
        self.assertEqual(enrich_daily('2099-01-01', {'date':'2099-01-01','games':{}}), 0)


if __name__ == '__main__':
    unittest.main()
