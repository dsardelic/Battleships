import pathlib
import re
import unittest

import battleships.puzzle


class IntegrationTests(unittest.TestCase):
    def test_puzzle_solutions(self):
        fixture_base_path = (
            pathlib.Path(battleships.__file__)
            .resolve()
            .parent.parent.joinpath("test/sample_files/")
        )
        for fixture_index in range(1, 16):
            fixture = "Battleships" + str(fixture_index).zfill(2)
            with self.subTest(fixture=fixture):
                puzzle = battleships.puzzle.Puzzle.load_puzzle(
                    fixture_base_path.joinpath(f"{fixture}.in")
                )
                battleships.puzzle.Puzzle.solutions = []
                puzzle.solve()
                with open(
                    fixture_base_path.joinpath(f"{fixture}.out"), "r", encoding="utf-8"
                ) as out_file:
                    out_file_content = out_file.read()
                solution_regex = r"╔═+╗\n(?:║(?:\s+[Ox.])+\s+║\n)+╚═+╝"
                self.assertEqual(
                    re.findall(solution_regex, out_file_content),
                    sorted(battleships.puzzle.Puzzle.solutions),
                )
