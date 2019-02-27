import pathlib
import unittest

import battleships
from battleships.puzzle import Puzzle


class IntegrationsTests(unittest.TestCase):
    @classmethod
    def get_solutions(cls, sample_input_file_name):
        puzzle = Puzzle.load_puzzle(
            pathlib.Path(battleships.__file__)
            .resolve()
            .parent.parent.joinpath("test/sample_files/")
            .joinpath(sample_input_file_name)
        )
        Puzzle.solutions = []
        puzzle.solve()
        return puzzle.solutions

    def test_for_input_file_01(self):
        self.assertEqual(
            set(self.get_solutions("Battleships01.in")),
            {
                "╔═════════════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   O   .   O   .   .   O   .   .  ║\n"
                "║  .   .   O   .   O   .   .   .   .   O  ║\n"
                "║  .   .   O   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   O   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   .   O   O  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  O   .   O   O   O   O   .   O   O   .  ║\n"
                "╚═════════════════════════════════════════╝",
                "╔═════════════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   O   .   O   .   .   .   .   O  ║\n"
                "║  .   .   O   .   O   .   .   O   .   .  ║\n"
                "║  .   .   O   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   O   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   .   O   O  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  O   .   O   O   O   O   .   O   O   .  ║\n"
                "╚═════════════════════════════════════════╝",
                "╔═════════════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   O   O   .   O   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   O   O   .  ║\n"
                "║  .   .   O   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   O   .   O   .   .   .   .   .  ║\n"
                "║  O   .   .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   O   O   O   O   .   O   O   O  ║\n"
                "╚═════════════════════════════════════════╝",
            },
        )

    def test_for_input_file_02(self):
        self.assertEqual(self.get_solutions("Battleships02.in"), [])

    def test_for_input_file_03(self):
        self.assertEqual(
            self.get_solutions("Battleships03.in"),
            [
                "╔═════════════════════════════════════════╗\n"
                "║  .   .   O   O   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   .   O   O   .   O   .  ║\n"
                "║  .   .   O   .   .   .   .   .   O   .  ║\n"
                "║  .   .   O   .   O   O   O   .   O   .  ║\n"
                "║  O   .   O   .   .   .   .   .   .   .  ║\n"
                "║  .   .   O   .   .   .   O   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   O   .   .   .   O   .   .   .  ║\n"
                "╚═════════════════════════════════════════╝"
            ],
        )

    def test_for_input_file_04(self):
        self.assertEqual(len(self.get_solutions("Battleships04.in")), 841)

    def test_for_input_file_05(self):
        self.assertEqual(
            self.get_solutions("Battleships05.in"),
            [
                "╔═════════════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   O   O   O   .  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   .   .   O   .   .   O   O   O  ║\n"
                "║  .   .   .   .   O   .   .   .   .   .  ║\n"
                "║  O   .   O   .   .   .   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   .   .   O   .   .   .  ║\n"
                "║  .   O   O   O   O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   .   .   .  ║\n"
                "╚═════════════════════════════════════════╝"
            ],
        )

    def test_for_input_file_06(self):
        self.assertEqual(
            self.get_solutions("Battleships06.in"),
            [
                "╔═════════════════════════╗\n"
                "║  O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   O   .  ║\n"
                "║  .   .   .   .   O   .  ║\n"
                "║  O   .   O   .   O   .  ║\n"
                "║  O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   O  ║\n"
                "╚═════════════════════════╝"
            ],
        )

    def test_for_input_file_07(self):
        self.assertEqual(
            set(self.get_solutions("Battleships07.in")),
            {
                "╔═════════════════════════╗\n"
                "║  .   O   .   O   .   O  ║\n"
                "║  .   O   .   O   .   .  ║\n"
                "║  .   .   .   O   .   O  ║\n"
                "║  .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   .   .  ║\n"
                "║  O   .   .   .   .   .  ║\n"
                "╚═════════════════════════╝",
                "╔═════════════════════════╗\n"
                "║  .   O   .   O   .   O  ║\n"
                "║  .   .   .   O   .   O  ║\n"
                "║  .   O   .   O   .   .  ║\n"
                "║  .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   .   .  ║\n"
                "║  O   .   .   .   .   .  ║\n"
                "╚═════════════════════════╝",
            },
        )

    def test_for_input_file_08(self):
        self.assertEqual(
            self.get_solutions("Battleships08.in"),
            [
                "╔═════════════════════════╗\n"
                "║  O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   O   O  ║\n"
                "║  .   .   .   .   .   .  ║\n"
                "║  O   .   .   .   O   .  ║\n"
                "║  O   .   .   .   .   .  ║\n"
                "║  O   .   .   O   O   .  ║\n"
                "╚═════════════════════════╝"
            ],
        )

    def test_for_input_file_09(self):
        self.assertEqual(
            self.get_solutions("Battleships09.in"),
            [
                "╔═════════════════════════╗\n"
                "║  O   .   .   .   .   O  ║\n"
                "║  O   .   .   O   .   .  ║\n"
                "║  O   .   .   .   .   .  ║\n"
                "║  .   .   O   .   .   O  ║\n"
                "║  .   .   O   .   .   O  ║\n"
                "║  O   .   .   .   .   .  ║\n"
                "╚═════════════════════════╝"
            ],
        )

    def test_for_input_file_10(self):
        self.assertEqual(
            self.get_solutions("Battleships10.in"),
            [
                "╔═════════════════════════════════╗\n"
                "║  O   .   .   O   O   .   O   .  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   .   .   .   O  ║\n"
                "║  .   .   .   O   .   O   .   .  ║\n"
                "║  O   .   .   .   .   O   .   .  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  O   O   O   O   .   .   .   .  ║\n"
                "║  .   .   .   .   .   .   O   O  ║\n"
                "╚═════════════════════════════════╝"
            ],
        )

    def test_for_input_file_11(self):
        self.assertEqual(
            set(self.get_solutions("Battleships11.in")),
            {
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   O   O   O   .   .  ║\n"
                "║  O   .   .   .   .   .   .   O  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   .   .   O   .   O  ║\n"
                "║  .   .   .   O   .   O   .   O  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   O   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  .   .   O   O   O   O   .   .  ║\n"
                "║  O   .   .   .   .   .   .   O  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   .   O   .   .  ║\n"
                "║  .   .   .   O   .   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   .   .   .   O   O   .   O  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   .   O   O   .   O  ║\n"
                "║  O   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   O   .   .   .   .  ║\n"
                "║  O   .   .   O   .   O   .   .  ║\n"
                "║  O   .   .   .   .   O   .   O  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   O   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   .   O   O   .   O  ║\n"
                "║  O   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  O   .   .   O   .   O   .   .  ║\n"
                "║  O   .   .   O   .   .   .   O  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   O   O   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
            },
        )

    def test_for_input_file_12(self):
        self.assertEqual(
            set(self.get_solutions("Battleships12.in")),
            {
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  O   .   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  .   O   O   .   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   .   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  .   O   O   .   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   O   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  .   .   O   O   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   O   O   .   O   O   .   .  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   O   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   O   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   .   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   .   O   .   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   O   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   .   O   .   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   .   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   O   O   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   O   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  .   .   O   .   .   O   .   O  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   O   O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   O   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  O   .   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   .   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   O   O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   .   O   O   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   O   O   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   .   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   O   O   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   O   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   .   O   O   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   O   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
            },
        )

    def test_for_input_file_13(self):
        self.assertEqual(
            self.get_solutions("Battleships13.in"),
            [
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  O   .   O   .   .   .   .   O  ║\n"
                "║  O   .   O   .   .   O   .   O  ║\n"
                "║  .   .   O   .   .   O   .   O  ║\n"
                "║  .   .   O   .   .   O   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   .  ║\n"
                "║  .   O   O   .   O   O   .   O  ║\n"
                "╚═════════════════════════════════╝"
            ],
        )

    def test_for_input_file_14(self):
        self.assertEqual(
            set(self.get_solutions("Battleships14.in")),
            {
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  .   O   O   O   .   .   O   .  ║\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  O   .   .   O   .   .   O   .  ║\n"
                "║  .   .   .   O   .   .   .   .  ║\n"
                "║  O   O   .   .   .   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   O   .   O   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  .   O   O   O   .   .   O   .  ║\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  O   .   .   O   .   .   O   .  ║\n"
                "║  .   .   .   O   .   .   .   .  ║\n"
                "║  O   O   .   O   .   .   .   O  ║\n"
                "║  .   .   .   .   .   O   .   .  ║\n"
                "║  .   O   O   .   .   O   .   O  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  .   O   O   O   .   .   O   .  ║\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  O   .   .   O   .   .   O   .  ║\n"
                "║  .   .   .   O   .   .   .   .  ║\n"
                "║  O   O   .   O   .   O   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   O   O   .   .   O   .   O  ║\n"
                "╚═════════════════════════════════╝",
            },
        )

    def test_for_input_file_15(self):
        self.assertEqual(
            set(self.get_solutions("Battleships15.in")),
            {
                "╔═════════════════════════════════╗\n"
                "║  O   .   .   O   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  O   O   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  O   .   O   .   .   .   O   .  ║\n"
                "║  .   .   O   .   .   .   O   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  O   .   O   O   O   O   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   O   O   .   O   .   .   O  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   O   .  ║\n"
                "║  O   .   .   .   O   .   O   .  ║\n"
                "║  .   .   O   .   O   .   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  O   O   O   .   O   .   O   .  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   O   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  O   .   .   .   O   .   O   .  ║\n"
                "║  O   .   O   .   .   .   .   .  ║\n"
                "╚═════════════════════════════════╝",
                "╔═════════════════════════════════╗\n"
                "║  O   O   O   .   O   .   O   .  ║\n"
                "║  .   .   .   .   O   .   .   .  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  .   .   O   O   O   O   .   O  ║\n"
                "║  .   .   .   .   .   .   .   O  ║\n"
                "║  O   .   .   .   .   .   .   .  ║\n"
                "║  O   .   .   .   O   .   O   .  ║\n"
                "║  .   .   O   .   O   .   .   .  ║\n"
                "╚═════════════════════════════════╝",
            },
        )
