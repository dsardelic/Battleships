import copy
import pathlib
import unittest.mock
from test.unit.test_board import parse_board
from test.unit.test_grid import parse_fieldtypegrid

import battleships
import params
from battleships.board import InvalidShipPlacementException
from battleships.fleet import Fleet
from battleships.grid import FieldType, Position, Series
from battleships.puzzle import Puzzle
from battleships.ship import Ship


class TestPuzzle(unittest.TestCase):
    def setUp(self):
        super().setUp()
        params.INPUT_FILE_NAME = "test/sample_files/Battleships01.in"
        self.sample_puzzle = Puzzle.load_puzzle(params.INPUT_FILE_PATH)
        Puzzle.solutions = []

    @classmethod
    def hashable_object_from_puzzle(cls, puzzle):
        return (
            (
                tuple(tuple(row) for row in puzzle.board.grid),
                frozenset(
                    {
                        series: tuple(number_of_ship_fields_to_mark)
                        for series, number_of_ship_fields_to_mark in (
                            puzzle.board.number_of_ship_fields_to_mark_in_series.items()
                        )
                    }
                ),
            ),
            frozenset(puzzle.fleet.items()),
        )

    def test___init__(self):
        puzzle = Puzzle(
            unittest.mock.sentinel.mock_board, unittest.mock.sentinel.mock_fleet
        )
        self.assertTrue(puzzle.board is unittest.mock.sentinel.mock_board)
        self.assertTrue(puzzle.fleet is unittest.mock.sentinel.mock_fleet)

    def test___eq__(self):
        puzzle1 = Puzzle(
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   .  ║(2)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(2)\n"
                "║  x   x   x   x   x  ║(3)\n"
                "╚═════════════════════╝\n"
                "  (2) (1) (4) (1) (4) "
            ),
            Fleet({4: 1, 3: 2, 1: 3}),
        )
        puzzle2 = Puzzle(
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   .  ║(2)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(2)\n"
                "║  x   x   x   x   x  ║(3)\n"
                "╚═════════════════════╝\n"
                "  (2) (1) (4) (1) (4) "
            ),
            Fleet({4: 1, 3: 2, 1: 3}),
        )

        puzzle2_orig = copy.deepcopy(puzzle2)
        self.assertTrue(puzzle1.__eq__(puzzle2))
        self.assertEqual(puzzle2, puzzle2_orig)

        puzzle2.board.grid[1][1] = FieldType.SEA
        puzzle2_orig = copy.deepcopy(puzzle2)
        self.assertFalse(puzzle1.__eq__(puzzle2))
        self.assertEqual(puzzle2, puzzle2_orig)

        puzzle2.board.grid[1][1] = FieldType.UNKNOWN
        puzzle2.fleet = Fleet({4: 1, 3: 1, 1: 3})
        puzzle2_orig = copy.deepcopy(puzzle2)
        self.assertFalse(puzzle1.__eq__(puzzle2))
        self.assertEqual(puzzle2, puzzle2_orig)

        self.assertFalse(puzzle1.__eq__("foo"))

    @unittest.mock.patch("battleships.puzzle.print")
    def test_parse_input_data_from_file(self, mocked_print):
        with unittest.mock.patch(
            "battleships.puzzle.open", side_effect=FileNotFoundError
        ):
            with self.assertRaises(FileNotFoundError):
                Puzzle.parse_input_data_from_file(unittest.mock.sentinel.path)
            mocked_print.assert_called_once_with(
                "Invalid input data file path.", file=Puzzle.ofile
            )

        mocked_print.reset_mock()
        actual_input_data = Puzzle.parse_input_data_from_file(params.INPUT_FILE_PATH)
        expected_grid = parse_fieldtypegrid(
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   O   x   x   x   x   x   x   x \n"
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   .   x   .   x   x   .   x   x \n"
            " x   x   x   x   x   x   x   x   x   x \n"
            " x   x   x   x   O   x   x   x   x   x "
        )
        expected_solution_ship_fields_in_rows = [0, 1, 3, 3, 1, 1, 2, 2, 0, 7]
        expected_solution_ship_fields_in_cols = [1, 1, 4, 1, 6, 1, 0, 2, 2, 2]
        expected_fleet = Fleet({4: 1, 3: 2, 2: 3, 1: 4})
        self.assertEqual(expected_grid, actual_input_data.grid)
        self.assertEqual(
            expected_solution_ship_fields_in_rows,
            actual_input_data.solution_ship_fields_in_rows,
        )
        self.assertEqual(
            expected_solution_ship_fields_in_cols,
            actual_input_data.solution_ship_fields_in_cols,
        )
        self.assertEqual(expected_fleet, actual_input_data.fleet)

    def test_load_puzzle(self):
        actual_puzzle = Puzzle.load_puzzle(params.INPUT_FILE_PATH)
        expected_puzzle = Puzzle(
            parse_board(
                "╔═════════════════════════════════════════╗\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(3)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(3)\n"
                "║  x   x   O   x   x   x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(2)\n"
                "║  x   x   .   x   .   x   x   .   x   x  ║(2)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   O   x   x   x   x   x  ║(6)\n"
                "╚═════════════════════════════════════════╝\n"
                "  (1) (1) (3) (1) (5) (1) (0) (2) (2) (2) "
            ),
            Fleet({4: 1, 3: 2, 2: 3, 1: 4}),
        )
        self.assertEqual(actual_puzzle.board, expected_puzzle.board)
        self.assertEqual(actual_puzzle.fleet, expected_puzzle.fleet)

        actual_puzzle = Puzzle.load_puzzle()
        expected_puzzle = Puzzle(
            parse_board(
                "╔═════════════════════════════════════════╗\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(3)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(3)\n"
                "║  x   x   O   x   x   x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(2)\n"
                "║  x   x   .   x   .   x   x   .   x   x  ║(2)\n"
                "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   O   x   x   x   x   x  ║(6)\n"
                "╚═════════════════════════════════════════╝\n"
                "  (1) (1) (3) (1) (5) (1) (0) (2) (2) (2) "
            ),
            Fleet({4: 1, 3: 2, 2: 3, 1: 4}),
        )
        self.assertEqual(actual_puzzle.board, expected_puzzle.board)
        self.assertEqual(actual_puzzle.fleet, expected_puzzle.fleet)

    def test_ship_group_exceeds_fleet(self):
        puzzle = Puzzle(unittest.mock.Mock(), Fleet({4: 1, 3: 2, 1: 1}))
        exceeding_ship_groups = (
            {Ship(unittest.mock.Mock(), 2, unittest.mock.Mock())},
            {
                Ship(unittest.mock.Mock(), 3, unittest.mock.Mock()),
                Ship(unittest.mock.Mock(), 3, unittest.mock.Mock()),
                Ship(unittest.mock.Mock(), 3, unittest.mock.Mock()),
            },
        )
        for ship_group in exceeding_ship_groups:
            with self.subTest():
                ship_group_orig = set(ship_group)
                self.assertTrue(puzzle.ship_group_exceeds_fleet(ship_group))
                self.assertEqual(ship_group, ship_group_orig)

        nonexceeding_ship_groups = (
            set(),
            {Ship(unittest.mock.Mock(), 3, unittest.mock.Mock())},
            {
                Ship(unittest.mock.Mock(), 4, unittest.mock.Mock()),
                Ship(unittest.mock.Mock(), 3, unittest.mock.Mock()),
                Ship(unittest.mock.Mock(), 3, unittest.mock.Mock()),
                Ship(unittest.mock.Mock(), 1, unittest.mock.Mock()),
            },
        )
        for ship_group in nonexceeding_ship_groups:
            with self.subTest():
                ship_group_orig = set(ship_group)
                self.assertFalse(puzzle.ship_group_exceeds_fleet(ship_group))
                self.assertEqual(ship_group, ship_group_orig)

    def test_get_possible_puzzles(self):
        puzzle = Puzzle(
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   .  ║(2)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(2)\n"
                "║  x   x   x   x   x  ║(3)\n"
                "╚═════════════════════╝\n"
                "  (2) (1) (4) (1) (4) "
            ),
            Fleet({5: 1}),
        )
        ships_occupying_position = puzzle.board.get_possible_ships_occupying_positions(
            {Position(3, 3)}, puzzle.fleet.distinct_ship_sizes
        )
        ships_occupying_position_orig = copy.deepcopy(ships_occupying_position)
        self.assertEqual(puzzle.get_possible_puzzles(ships_occupying_position), [])
        self.assertEqual(ships_occupying_position, ships_occupying_position_orig)

        puzzle = Puzzle(
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   x   x   x   x  ║(0)\n"
                "║  x   x   x   x   .  ║(2)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(2)\n"
                "║  x   x   x   x   x  ║(3)\n"
                "╚═════════════════════╝\n"
                "  (2) (1) (4) (1) (4) "
            ),
            Fleet({4: 1, 3: 2, 1: 3}),
        )
        ships_occupying_position = puzzle.board.get_possible_ships_occupying_positions(
            {Position(2, 1), Position(3, 3), Position(5, 3)},
            puzzle.fleet.distinct_ship_sizes,
        )
        ships_occupying_position_orig = copy.deepcopy(ships_occupying_position)
        actual_possible_puzzles_list = puzzle.get_possible_puzzles(
            ships_occupying_position
        )
        self.assertEqual(ships_occupying_position, ships_occupying_position_orig)
        expected_possible_puzzles_list = [
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  .   .   .   .   .  ║(0)\n"
                    "║  O   .   .   .   .  ║(1)\n"
                    "║  .   .   O   .   x  ║(1)\n"
                    "║  .   .   .   .   x  ║(2)\n"
                    "║  O   O   O   .   .  ║(0)\n"
                    "╚═════════════════════╝\n"
                    "  (0) (0) (2) (1) (4) "
                ),
                Fleet({4: 1, 3: 1, 1: 1}),
            ),
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  .   .   .   .   .  ║(0)\n"
                    "║  O   .   .   .   .  ║(1)\n"
                    "║  .   .   O   .   x  ║(1)\n"
                    "║  .   .   .   .   .  ║(2)\n"
                    "║  .   O   O   O   .  ║(0)\n"
                    "╚═════════════════════╝\n"
                    "  (1) (0) (2) (0) (4) "
                ),
                Fleet({4: 1, 3: 1, 1: 1}),
            ),
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  .   .   .   .   .  ║(0)\n"
                    "║  O   .   .   .   .  ║(1)\n"
                    "║  .   .   O   .   x  ║(1)\n"
                    "║  x   .   .   .   .  ║(2)\n"
                    "║  .   .   O   O   O  ║(0)\n"
                    "╚═════════════════════╝\n"
                    "  (1) (1) (2) (0) (3) "
                ),
                Fleet({4: 1, 3: 1, 1: 1}),
            ),
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  .   .   .   .   .  ║(0)\n"
                    "║  O   .   .   .   .  ║(1)\n"
                    "║  .   .   O   .   x  ║(1)\n"
                    "║  x   .   .   .   x  ║(2)\n"
                    "║  x   .   O   .   x  ║(2)\n"
                    "╚═════════════════════╝\n"
                    "  (1) (1) (2) (1) (4) "
                ),
                Fleet({4: 1, 3: 2}),
            ),
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  .   .   .   .   .  ║(0)\n"
                    "║  O   .   O   .   .  ║(0)\n"
                    "║  .   .   O   .   x  ║(1)\n"
                    "║  x   .   O   .   x  ║(1)\n"
                    "║  x   .   O   .   x  ║(2)\n"
                    "╚═════════════════════╝\n"
                    "  (1) (1) (0) (1) (4) "
                ),
                Fleet({3: 2, 1: 2}),
            ),
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  .   .   .   .   .  ║(0)\n"
                    "║  O   .   .   .   .  ║(1)\n"
                    "║  .   .   O   .   x  ║(1)\n"
                    "║  x   .   O   .   x  ║(1)\n"
                    "║  x   .   O   .   x  ║(2)\n"
                    "╚═════════════════════╝\n"
                    "  (1) (1) (1) (1) (4) "
                ),
                Fleet({4: 1, 3: 1, 1: 2}),
            ),
        ]
        self.assertEqual(
            {
                self.__class__.hashable_object_from_puzzle(puzzle)
                for puzzle in actual_possible_puzzles_list
            },
            {
                self.__class__.hashable_object_from_puzzle(puzzle)
                for puzzle in expected_possible_puzzles_list
            },
        )

    def test_mark_subfleet_of_biggest_remaining_ships(self):
        board_repr = (
            "╔═════════════════════╗\n"
            "║  x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   .  ║(2)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(2)\n"
            "║  x   x   x   x   x  ║(3)\n"
            "╚═════════════════════╝\n"
            "  (2) (1) (4) (1) (4) "
        )

        fleet1 = Fleet({})
        puzzle1 = Puzzle(parse_board(board_repr), Fleet(fleet1))
        puzzle1.mark_subfleet_of_biggest_remaining_ships()
        self.assertEqual(puzzle1.board, parse_board(board_repr))
        self.assertEqual(puzzle1.fleet, fleet1)
        self.assertEqual(
            puzzle1.__class__.solutions,
            [
                "╔═════════════════════╗\n"
                "║  x   x   x   x   x  ║\n"
                "║  x   x   x   x   .  ║\n"
                "║  x   x   x   x   x  ║\n"
                "║  x   .   x   x   x  ║\n"
                "║  x   x   x   x   x  ║\n"
                "╚═════════════════════╝"
            ],
        )

        fleet2 = Fleet({4: 1, 3: 2, 1: 1})
        puzzle2 = Puzzle(parse_board(board_repr), Fleet(fleet2))
        with unittest.mock.patch.object(
            battleships.puzzle.Puzzle, "mark_ship_group"
        ) as mocked_try_to_mark_ship_group:
            puzzle2.mark_subfleet_of_biggest_remaining_ships()
            self.assertEqual(puzzle2, Puzzle(parse_board(board_repr), Fleet(fleet2)))
            mocked_try_to_mark_ship_group.assert_called_once_with(
                {Ship(Position(2, 3), 4, Series.COLUMN)}
            )

        fleet3 = Fleet({3: 2, 1: 1})
        puzzle3 = Puzzle(parse_board(board_repr), Fleet(fleet3))
        with unittest.mock.patch.object(
            battleships.puzzle.Puzzle, "mark_ship_group"
        ) as mocked_try_to_mark_ship_group:
            puzzle3.mark_subfleet_of_biggest_remaining_ships()
            self.assertEqual(puzzle3, Puzzle(parse_board(board_repr), Fleet(fleet3)))
            self.assertEqual(mocked_try_to_mark_ship_group.call_count, 15)
            mocked_try_to_mark_ship_group.assert_has_calls(
                [
                    unittest.mock.call(
                        {
                            Ship(Position(5, 1), 3, Series.ROW),
                            Ship(Position(5, 2), 3, Series.ROW),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 1), 3, Series.ROW),
                            Ship(Position(5, 3), 3, Series.ROW),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 1), 3, Series.ROW),
                            Ship(Position(2, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 1), 3, Series.ROW),
                            Ship(Position(3, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 1), 3, Series.ROW),
                            Ship(Position(3, 5), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 2), 3, Series.ROW),
                            Ship(Position(5, 3), 3, Series.ROW),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 2), 3, Series.ROW),
                            Ship(Position(2, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 2), 3, Series.ROW),
                            Ship(Position(3, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 2), 3, Series.ROW),
                            Ship(Position(3, 5), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 3), 3, Series.ROW),
                            Ship(Position(2, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 3), 3, Series.ROW),
                            Ship(Position(3, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(5, 3), 3, Series.ROW),
                            Ship(Position(3, 5), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(2, 3), 3, Series.COLUMN),
                            Ship(Position(3, 3), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(2, 3), 3, Series.COLUMN),
                            Ship(Position(3, 5), 3, Series.COLUMN),
                        }
                    ),
                    unittest.mock.call(
                        {
                            Ship(Position(3, 3), 3, Series.COLUMN),
                            Ship(Position(3, 5), 3, Series.COLUMN),
                        }
                    ),
                ],
                any_order=True,
            )

    @unittest.mock.patch.object(battleships.puzzle.Puzzle, "decide_how_to_proceed")
    def test_mark_ship_group(self, mocked_decide_how_to_proceed):
        board_repr = (
            "╔═════════════════════╗\n"
            "║  x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   .  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(2)\n"
            "║  x   x   x   x   x  ║(3)\n"
            "╚═════════════════════╝\n"
            "  (2) (1) (4) (1) (4) "
        )
        fleet = Fleet({4: 1, 3: 2, 1: 2})

        puzzle = Puzzle(parse_board(board_repr), Fleet.get_copy_of(fleet))
        ship_group = {
            Ship(Position(1, 3), 4, Series.COLUMN),
            Ship(Position(2, 3), 4, Series.COLUMN),
        }
        with self.assertRaises(InvalidShipPlacementException):
            puzzle.mark_ship_group(ship_group)

        # test when board is overmarked
        puzzle = Puzzle(parse_board(board_repr), Fleet.get_copy_of(fleet))
        ship_group = {
            Ship(Position(5, 2), 1, Series.ROW),
            Ship(Position(5, 4), 1, Series.ROW),
        }
        ship_group_orig = set(ship_group)
        puzzle.mark_ship_group(ship_group)
        self.assertEqual(
            puzzle.board,
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   .   x   .   x  ║(1)\n"
                "║  x   .   x   .   .  ║(1)\n"
                "║  x   .   x   .   x  ║(2)\n"
                "║  .   .   .   .   .  ║(2)\n"
                "║  .   O   .   O   .  ║(1)\n"
                "╚═════════════════════╝\n"
                "  (2) (0) (4) (0) (4) "
            ),
        )
        self.assertEqual(ship_group, ship_group_orig)
        mocked_decide_how_to_proceed.assert_not_called()

        mocked_decide_how_to_proceed.reset_mock()
        puzzle = Puzzle(parse_board(board_repr), Fleet.get_copy_of(fleet))
        fleet = Fleet({4: 1, 3: 2, 1: 2})
        ship_group = {
            Ship(Position(3, 3), 3, Series.COLUMN),
            Ship(Position(3, 5), 3, Series.COLUMN),
        }
        ship_group_orig = set(ship_group)
        puzzle.mark_ship_group(ship_group)
        self.assertEqual(
            puzzle,
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  x   x   x   x   x  ║(1)\n"
                    "║  x   .   .   .   .  ║(1)\n"
                    "║  .   .   O   .   O  ║(0)\n"
                    "║  .   .   O   .   O  ║(0)\n"
                    "║  x   .   O   .   O  ║(1)\n"
                    "╚═════════════════════╝\n"
                    "  (2) (1) (1) (1) (1) "
                ),
                Fleet({4: 1, 1: 2}),
            ),
        )
        self.assertEqual(ship_group, ship_group_orig)
        mocked_decide_how_to_proceed.assert_called_once()

    @unittest.mock.patch.object(
        battleships.puzzle.Puzzle, "decide_how_to_proceed", autospec=True
    )
    def test_try_to_cover_all_ship_fields_to_be(self, mocked_decide_how_to_proceed):
        board_repr = (
            "╔═════════════════════╗\n"
            "║  x   x   .   x   x  ║(1)\n"
            "║  x   x   x   x   .  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(2)\n"
            "║  x   x   x   x   x  ║(3)\n"
            "╚═════════════════════╝\n"
            "  (2) (1) (4) (1) (4) "
        )
        fleet = Fleet({4: 1, 3: 1, 2: 1})

        puzzle = Puzzle(parse_board(board_repr), Fleet.get_copy_of(fleet))
        positions = {Position(1, 5)}
        positions_orig = set(positions)
        puzzle.try_to_cover_all_ship_fields_to_be(positions)
        self.assertEqual(positions, positions_orig)
        mocked_decide_how_to_proceed.assert_not_called()

        puzzle = Puzzle(parse_board(board_repr), Fleet.get_copy_of(fleet))
        positions = {Position(2, 3), Position(4, 3), Position(3, 5), Position(5, 5)}
        positions_orig = set(positions)
        puzzle.try_to_cover_all_ship_fields_to_be(positions)
        self.assertEqual(
            puzzle,
            Puzzle(
                parse_board(
                    "╔═════════════════════╗\n"
                    "║  x   .   .   .   x  ║(1)\n"
                    "║  .   .   O   .   .  ║(0)\n"
                    "║  .   .   O   .   O  ║(0)\n"
                    "║  .   .   O   .   O  ║(0)\n"
                    "║  x   .   O   .   O  ║(1)\n"
                    "╚═════════════════════╝\n"
                    "  (2) (1) (0) (1) (1) "
                ),
                Fleet({2: 1}),
            ),
        )
        self.assertEqual(positions, positions_orig)
        mocked_decide_how_to_proceed.assert_called_once()

        mocked_decide_how_to_proceed.reset_mock()
        puzzle = Puzzle(parse_board(board_repr), Fleet.get_copy_of(fleet))
        positions = {Position(5, 3), Position(5, 5)}
        positions_orig = set({Position(5, 3), Position(5, 5)})
        puzzle.try_to_cover_all_ship_fields_to_be(positions)
        self.assertEqual(mocked_decide_how_to_proceed.call_count, 6)
        mocked_decide_how_to_proceed.assert_has_calls(
            [
                unittest.mock.call(
                    Puzzle(
                        parse_board(
                            "╔═════════════════════╗\n"
                            "║  x   .   .   .   x  ║(1)\n"
                            "║  .   .   O   .   .  ║(0)\n"
                            "║  .   .   O   .   O  ║(0)\n"
                            "║  .   .   O   .   O  ║(0)\n"
                            "║  x   .   O   .   O  ║(1)\n"
                            "╚═════════════════════╝\n"
                            "  (2) (1) (0) (1) (1) "
                        ),
                        Fleet({2: 1}),
                    )
                ),
                unittest.mock.call(
                    Puzzle(
                        parse_board(
                            "╔═════════════════════╗\n"
                            "║  x   x   .   x   x  ║(1)\n"
                            "║  x   x   x   .   .  ║(1)\n"
                            "║  x   .   .   .   O  ║(1)\n"
                            "║  .   .   O   .   O  ║(0)\n"
                            "║  x   .   O   .   O  ║(1)\n"
                            "╚═════════════════════╝\n"
                            "  (2) (1) (2) (1) (1) "
                        ),
                        Fleet({4: 1}),
                    )
                ),
                unittest.mock.call(
                    Puzzle(
                        parse_board(
                            "╔═════════════════════╗\n"
                            "║  x   .   .   x   x  ║(1)\n"
                            "║  x   .   x   .   .  ║(1)\n"
                            "║  x   .   x   .   O  ║(1)\n"
                            "║  .   .   .   .   O  ║(1)\n"
                            "║  .   O   O   .   O  ║(0)\n"
                            "╚═════════════════════╝\n"
                            "  (2) (0) (3) (1) (1) "
                        ),
                        Fleet({4: 1}),
                    )
                ),
                unittest.mock.call(
                    Puzzle(
                        parse_board(
                            "╔═════════════════════╗\n"
                            "║  x   .   .   .   x  ║(1)\n"
                            "║  .   .   O   .   .  ║(0)\n"
                            "║  x   .   O   .   .  ║(1)\n"
                            "║  .   .   O   .   O  ║(0)\n"
                            "║  x   .   O   .   O  ║(1)\n"
                            "╚═════════════════════╝\n"
                            "  (2) (1) (0) (1) (2) "
                        ),
                        Fleet({3: 1}),
                    )
                ),
                unittest.mock.call(
                    Puzzle(
                        parse_board(
                            "╔═════════════════════╗\n"
                            "║  x   x   .   x   x  ║(1)\n"
                            "║  x   .   .   .   .  ║(1)\n"
                            "║  x   .   O   .   .  ║(1)\n"
                            "║  .   .   O   .   O  ║(0)\n"
                            "║  x   .   O   .   O  ║(1)\n"
                            "╚═════════════════════╝\n"
                            "  (2) (1) (1) (1) (2) "
                        ),
                        Fleet({4: 1}),
                    )
                ),
                unittest.mock.call(
                    Puzzle(
                        parse_board(
                            "╔═════════════════════╗\n"
                            "║  x   x   .   .   x  ║(1)\n"
                            "║  x   x   x   .   .  ║(1)\n"
                            "║  x   x   x   .   x  ║(2)\n"
                            "║  x   .   .   .   .  ║(2)\n"
                            "║  .   .   O   O   O  ║(0)\n"
                            "╚═════════════════════╝\n"
                            "  (2) (1) (3) (0) (3) "
                        ),
                        Fleet({4: 1, 2: 1}),
                    )
                ),
            ],
            any_order=True,
        )
        self.assertEqual(positions, positions_orig)

    @unittest.mock.patch.object(
        battleships.puzzle.Puzzle, "mark_subfleet_of_biggest_remaining_ships"
    )
    @unittest.mock.patch.object(
        battleships.puzzle.Puzzle, "try_to_cover_all_ship_fields_to_be"
    )
    @unittest.mock.patch.object(
        battleships.board.Board, "find_definite_ship_fields_positions"
    )
    def test_decide_how_to_proceed(
        self,
        mocked_find_definite_ship_fields_positions,
        mocked_try_to_cover_all_ship_fields_to_be,
        mocked_mark_subfleet_of_biggest_remaining_ships,
    ):
        mocked_find_definite_ship_fields_positions.side_effect = (
            set(),
            set(),
            {Position(3, 3)},
            {Position(3, 3)},
        )

        positions = set()
        positions_orig = set()
        self.sample_puzzle.decide_how_to_proceed(positions)
        self.assertEqual(positions, positions_orig)
        mocked_try_to_cover_all_ship_fields_to_be.assert_not_called()
        mocked_mark_subfleet_of_biggest_remaining_ships.assert_called_once_with()
        mocked_try_to_cover_all_ship_fields_to_be.reset_mock()
        mocked_mark_subfleet_of_biggest_remaining_ships.reset_mock()

        positions = {Position(5, 3)}
        positions_orig = set(positions)
        self.sample_puzzle.decide_how_to_proceed(positions)
        self.assertEqual(positions, positions_orig)
        mocked_try_to_cover_all_ship_fields_to_be.assert_called_once_with(
            {Position(5, 3)}
        )
        mocked_mark_subfleet_of_biggest_remaining_ships.assert_not_called()
        mocked_try_to_cover_all_ship_fields_to_be.reset_mock()
        mocked_mark_subfleet_of_biggest_remaining_ships.reset_mock()

        positions = set()
        positions_orig = set(positions)
        self.sample_puzzle.decide_how_to_proceed(positions)
        self.assertEqual(positions, positions_orig)
        mocked_try_to_cover_all_ship_fields_to_be.assert_called_once_with(
            {Position(3, 3)}
        )
        mocked_mark_subfleet_of_biggest_remaining_ships.assert_not_called()
        mocked_try_to_cover_all_ship_fields_to_be.reset_mock()
        mocked_mark_subfleet_of_biggest_remaining_ships.reset_mock()

        positions = set({Position(5, 3)})
        positions_orig = set(positions)
        self.sample_puzzle.decide_how_to_proceed(positions)
        self.assertEqual(positions, positions_orig)
        mocked_try_to_cover_all_ship_fields_to_be.assert_called_once_with(
            {Position(5, 3), Position(3, 3)}
        )
        mocked_mark_subfleet_of_biggest_remaining_ships.assert_not_called()

    def test_solve(self):
        fleet = Fleet({3: 1, 2: 2, 1: 2})
        puzzle = Puzzle(
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (0) (2) (1) (2) "
            ),
            Fleet(fleet),
        )
        with unittest.mock.patch.object(
            battleships.puzzle.Puzzle, "decide_how_to_proceed"
        ) as mock_decide_how_to_proceed:
            puzzle.solve()
        self.assertEqual(
            puzzle.board,
            parse_board(
                "╔═════════════════════╗\n"
                "║  x   .   x   x   .  ║(3)\n"
                "║  x   .   x   .   x  ║(2)\n"
                "║  x   .   x   x   x  ║(3)\n"
                "║  x   .   x   .   x  ║(1)\n"
                "║  x   .   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (0) (3) (1) (2) "
            ),
        )
        self.assertEqual(puzzle.fleet, fleet)
        mock_decide_how_to_proceed.assert_called_once_with({Position(3, 3)})

    @unittest.mock.patch("battleships.puzzle.print")
    def test_print_solutions(self, mocked_print):
        Puzzle.solutions = []
        self.sample_puzzle.print_solutions()
        mocked_print.assert_called_once_with("No solutions found.", file=Puzzle.ofile)

        mocked_print.reset_mock()
        self.sample_puzzle.__class__.solutions = ["C", "B", "A"]
        self.sample_puzzle.print_solutions()
        self.assertEqual(
            mocked_print.mock_calls,
            [
                unittest.mock.call("A", "\n", file=Puzzle.ofile),
                unittest.mock.call("B", "\n", file=Puzzle.ofile),
                unittest.mock.call("C", "\n", file=Puzzle.ofile),
                unittest.mock.call("3 solutions in total.", file=Puzzle.ofile),
            ],
        )

    def test_run(self):
        import io

        actual_ofile = io.StringIO()
        battleships.puzzle.Puzzle.run(actual_ofile)
        with open(
            pathlib.Path(params.__file__)
            .resolve()
            .parent.joinpath("test/sample_files/Battleships01.out"),
            "r",
            encoding="utf-8",
        ) as expected_ofile:
            self.assertEqual(actual_ofile.getvalue(), expected_ofile.read())
