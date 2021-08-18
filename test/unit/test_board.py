import copy
import random
import re
import unittest.mock
from test.unit.test_grid import parse_fieldtypegrid

from battleships.board import Board, InvalidShipPlacementException
from battleships.grid import FieldType, FieldTypeGrid, Position, Series
from battleships.ship import Ship


def parse_board(board_repr):
    visible_grid_repr = ""
    number_of_ship_fields_to_mark_in_rows = []
    repr_string_lines = board_repr.split("\n")
    for line_number, line in enumerate(repr_string_lines[1:], 1):
        if re.fullmatch(r"^╚═+╝$", line):
            number_of_ship_fields_to_mark_in_columns = [
                int(x) for x in re.findall(r"\d+", repr_string_lines[line_number + 1])
            ]
            break
        match = re.fullmatch(r"^║ (.+) ║\((\d+)\)$", line)
        visible_grid_repr += match.group(1) + "\n"
        number_of_ship_fields_to_mark_in_rows.append(int(match.group(2)))
    visible_grid = parse_fieldtypegrid(visible_grid_repr.strip("\n"))
    grid = FieldTypeGrid(
        [[FieldType.SEA] * (len(visible_grid[0]) + 2)]
        + [[FieldType.SEA, *row, FieldType.SEA] for row in visible_grid]
        + [[FieldType.SEA] * (len(visible_grid[0]) + 2)]
    )
    return Board(
        grid,
        {
            Series.ROW: [0, *number_of_ship_fields_to_mark_in_rows, 0],
            Series.COLUMN: [0, *number_of_ship_fields_to_mark_in_columns, 0],
        },
    )


class TestBoard(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sample_board_repr = (
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   .   .   .   O   .   .   .   .   .  ║(1)\n"
            "║  .   .   O   .   O   .   .   x   .   .  ║(0)\n"
            "║  .   .   O   .   O   .   x   .   .   O  ║(3)\n"
            "║  x   .   O   .   .   .   x   .   .   .  ║(0)\n"
            "║  .   .   .   .   O   .   x   .   .   .  ║(4)\n"
            "║  .   x   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  x   .   .   x   .   .   .   .   O   O  ║(0)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(5)\n"
            "║  O   .   O   O   O   O   .   O   O   .  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (1) (3) (3) (4) (5) (0) (0) (1) "
        )
        self.sample_board = parse_board(self.sample_board_repr)

    def test___init__(self):
        board = Board(
            unittest.mock.sentinel.grid,
            unittest.mock.sentinel.number_of_ship_fields_to_mark_in_series,
        )
        self.assertTrue(board.grid is unittest.mock.sentinel.grid)
        self.assertTrue(
            board.number_of_ship_fields_to_mark_in_series
            is unittest.mock.sentinel.number_of_ship_fields_to_mark_in_series
        )

    @unittest.mock.patch.object(Board, "repr")
    def test___repr__(self, mock_repr):
        self.sample_board.__repr__()
        mock_repr.assert_called_once_with(True)

    def test___eq__(self):
        other_board = parse_board(self.sample_board_repr)
        other_board_orig = Board.get_copy_of(other_board)
        self.assertTrue(self.sample_board.__eq__(other_board))
        self.assertEqual(other_board, other_board_orig)

        other_board.grid[1][1] = FieldType.UNKNOWN
        other_board_orig = Board.get_copy_of(other_board)
        self.assertFalse(self.sample_board.__eq__(other_board))
        self.assertEqual(other_board, other_board_orig)

        other_board.grid[1][1] = FieldType.SEA
        other_board_orig = Board.get_copy_of(other_board)
        self.assertTrue(self.sample_board.__eq__(other_board))
        self.assertEqual(other_board, other_board_orig)

        other_board.number_of_ship_fields_to_mark_in_series[Series.ROW][6] = 5
        other_board_orig = Board.get_copy_of(other_board)
        self.assertFalse(self.sample_board.__eq__(other_board))
        self.assertEqual(other_board, other_board_orig)

        self.assertFalse(self.sample_board.__eq__(self.sample_board.grid))

    def test_parse_board(self):
        input_grid = parse_fieldtypegrid(
            " .   .   .   .   .   .   .   .   .   . \n"
            " x   .   .   .   O   .   .   .   .   . \n"
            " .   .   O   .   O   .   .   x   .   . \n"
            " .   .   O   .   O   .   x   .   .   O \n"
            " x   .   O   .   .   .   x   .   .   . \n"
            " .   .   .   .   O   .   x   .   .   . \n"
            " .   x   .   .   O   .   x   .   .   . \n"
            " x   .   .   x   .   .   .   .   O   O \n"
            " .   .   .   .   .   .   .   .   .   . \n"
            " O   .   O   O   O   O   .   O   O   . "
        )
        input_number_of_ship_fields_to_mark_in_rows = [0, 2, 2, 6, 1, 5, 1, 2, 5, 7]
        input_number_of_ship_fields_to_mark_in_cols = [2, 1, 5, 4, 9, 5, 5, 1, 2, 3]

        input_grid_orig = input_grid
        input_number_of_ship_fields_to_mark_in_rows_orig = (
            input_number_of_ship_fields_to_mark_in_rows
        )
        input_number_of_ship_fields_to_mark_in_cols_orig = (
            input_number_of_ship_fields_to_mark_in_cols
        )

        parsed_board = Board.parse_board(
            input_grid,
            input_number_of_ship_fields_to_mark_in_rows,
            input_number_of_ship_fields_to_mark_in_cols,
        )
        self.assertEqual(self.sample_board, parsed_board)
        self.assertFalse(input_grid is parsed_board.grid)
        self.assertEqual(input_grid, input_grid_orig)
        self.assertFalse(
            input_number_of_ship_fields_to_mark_in_rows
            is parsed_board.number_of_ship_fields_to_mark_in_series[Series.ROW]
        )
        self.assertEqual(
            input_number_of_ship_fields_to_mark_in_rows,
            input_number_of_ship_fields_to_mark_in_rows_orig,
        )
        self.assertFalse(
            input_number_of_ship_fields_to_mark_in_cols
            is parsed_board.number_of_ship_fields_to_mark_in_series[Series.COLUMN]
        )
        self.assertEqual(
            input_number_of_ship_fields_to_mark_in_cols,
            input_number_of_ship_fields_to_mark_in_cols_orig,
        )

    def test_get_copy_of(self):
        sample_board_orig = copy.deepcopy(self.sample_board)
        actual_copy = Board.get_copy_of(self.sample_board)
        self.assertFalse(actual_copy is self.sample_board)
        self.assertEqual(actual_copy, self.sample_board)
        self.assertEqual(self.sample_board, sample_board_orig)

    def test_size(self):
        self.assertEqual(self.sample_board.size, 12)

        board = parse_board(
            "╔═════════════╗\n"
            "║  .   .   .  ║(0)\n"
            "║  x   .   .  ║(1)\n"
            "║  .   .   O  ║(0)\n"
            "╚═════════════╝\n"
            "  (1) (1) (1) "
        )
        self.assertEqual(board.size, 5)

    def test_repr(self):
        self.assertEqual(self.sample_board_repr, self.sample_board.repr(True))

        expected_board_repr = (
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║\n"
            "║  x   .   .   .   O   .   .   .   .   .  ║\n"
            "║  .   .   O   .   O   .   .   x   .   .  ║\n"
            "║  .   .   O   .   O   .   x   .   .   O  ║\n"
            "║  x   .   O   .   .   .   x   .   .   .  ║\n"
            "║  .   .   .   .   O   .   x   .   .   .  ║\n"
            "║  .   x   .   .   O   .   x   .   .   .  ║\n"
            "║  x   .   .   x   .   .   .   .   O   O  ║\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║\n"
            "║  O   .   O   O   O   O   .   O   O   .  ║\n"
            "╚═════════════════════════════════════════╝"
        )
        self.assertEqual(expected_board_repr, self.sample_board.repr(False))

        expected_board_repr += "\n"
        self.assertNotEqual(expected_board_repr, self.sample_board.repr(False))

    def test_set_ship_fields_as_unknown(self):
        actual_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   .   .   .   O   .   .   .   .   .  ║(0)\n"
            "║  .   .   O   .   O   .   .   x   .   .  ║(0)\n"
            "║  .   .   O   .   O   .   x   .   .   O  ║(0)\n"
            "║  x   .   O   .   .   .   x   .   .   .  ║(0)\n"
            "║  .   .   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  .   x   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  x   .   .   x   .   .   .   .   O   O  ║(0)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  O   .   O   O   O   O   .   O   O   .  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (0) (0) (0) (0) (0) (0) (0) (0) (0) (0) "
        )
        ship_fields = {
            Position(3, 3),
            Position(4, 3),
            Position(5, 3),
            Position(10, 3),
            Position(10, 6),
            Position(8, 9),
            Position(8, 10),
        }
        ship_fields_orig = set(ship_fields)
        actual_board.set_ship_fields_as_unknown(ship_fields)
        expected_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   .   .   .   O   .   .   .   .   .  ║(0)\n"
            "║  .   .   x   .   O   .   .   x   .   .  ║(1)\n"
            "║  .   .   x   .   O   .   x   .   .   O  ║(1)\n"
            "║  x   .   x   .   .   .   x   .   .   .  ║(1)\n"
            "║  .   .   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  .   x   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  x   .   .   x   .   .   .   .   x   x  ║(2)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  O   .   x   O   O   x   .   O   O   .  ║(2)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (0) (0) (4) (0) (0) (1) (0) (0) (1) (1) "
        )
        self.assertEqual(expected_board, actual_board)
        self.assertEqual(ship_fields, ship_fields_orig)

    def test_get_ship_fields_positions(self):
        board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   .   .   .   O   .   .   .   .   .  ║(0)\n"
            "║  .   .   x   .   O   .   .   x   .   .  ║(1)\n"
            "║  .   .   x   .   O   .   x   .   .   O  ║(1)\n"
            "║  x   .   x   .   .   .   x   .   .   .  ║(1)\n"
            "║  .   .   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  .   x   .   .   O   .   x   .   .   .  ║(0)\n"
            "║  x   .   .   x   .   .   .   .   x   x  ║(2)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  O   .   x   O   O   x   .   O   O   .  ║(2)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (0) (0) (4) (0) (0) (1) (0) (0) (1) (1) "
        )
        self.assertEqual(
            {
                Position(10, 1),
                Position(10, 4),
                Position(10, 5),
                Position(10, 8),
                Position(10, 9),
                Position(4, 10),
                Position(2, 5),
                Position(3, 5),
                Position(4, 5),
                Position(6, 5),
                Position(7, 5),
            },
            board.get_ship_fields_positions(),
        )

    def test_mark_sea_in_series_with_no_rem_ship_fields(self):
        actual_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   .   x   x   x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   .   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   .   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   .   x   O   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (4) (0) (0) (0) (0) "
        )
        actual_board.mark_sea_in_series_with_no_rem_ship_fields()
        expected_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   x   .   .   .   x   .   .   .   .  ║(2)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   x   .   .   .   x   .   .   .   .  ║(1)\n"
            "║  x   x   .   .   .   x   .   .   .   .  ║(1)\n"
            "║  x   x   .   .   .   x   .   .   .   .  ║(1)\n"
            "║  x   x   .   .   .   x   .   .   .   .  ║(1)\n"
            "║  .   .   .   .   .   .   .   .   O   .  ║(0)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (4) (0) (0) (0) (0) "
        )
        self.assertEqual(expected_board, actual_board)

    def test_mark_diagonal_sea_fields_for_positions(self):
        actual_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   .   x   x   x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   .   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   .   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (4) (0) (0) (0) (0) "
        )
        positions = {Position(5, 9), Position(2, 1), Position(10, 10)}
        positions_orig = set(positions)
        actual_board.mark_diagonal_sea_fields_for_positions(positions)
        expected_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   .   x   x   x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   .   x   .   x   .  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   .   x   .  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   .   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   .   x   .   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (4) (0) (0) (0) (0) "
        )
        self.assertEqual(expected_board, actual_board)
        self.assertEqual(positions, positions_orig)

    def test_ship_is_within_playable_grid(self):
        board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   .   x   x   x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   .   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   .   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (4) (0) (0) (0) (0) "
        )

        ships_within_playable_grid = (
            Ship(Position(1, 1), 3, Series.ROW),
            Ship(Position(1, 8), 3, Series.ROW),
            Ship(Position(5, 5), 3, Series.ROW),
            Ship(Position(10, 5), 3, Series.ROW),
            Ship(Position(1, 1), 3, Series.COLUMN),
            Ship(Position(8, 1), 3, Series.COLUMN),
            Ship(Position(5, 5), 3, Series.COLUMN),
            Ship(Position(5, 10), 3, Series.COLUMN),
            Ship(Position(1, 1), 1, Series.ROW),
            Ship(Position(6, 6), 1, Series.ROW),
            Ship(Position(10, 10), 1, Series.ROW),
        )
        for ship in ships_within_playable_grid:
            with self.subTest(ship):
                self.assertTrue(board.ship_is_within_playable_grid(ship))

        ships_outside_playable_grid = (
            Ship(Position(-1, 4), 3, Series.ROW),
            Ship(Position(0, 4), 3, Series.ROW),
            Ship(Position(1, 0), 3, Series.ROW),
            Ship(Position(1, 9), 3, Series.ROW),
            Ship(Position(11, 5), 3, Series.ROW),
            Ship(Position(4, -1), 3, Series.COLUMN),
            Ship(Position(4, 0), 3, Series.COLUMN),
            Ship(Position(0, 1), 3, Series.COLUMN),
            Ship(Position(9, 1), 3, Series.COLUMN),
            Ship(Position(5, 11), 3, Series.COLUMN),
            Ship(Position(0, 1), 1, Series.ROW),
            Ship(Position(1, 0), 1, Series.ROW),
            Ship(Position(11, 10), 1, Series.ROW),
            Ship(Position(10, 11), 1, Series.ROW),
        )
        for ship in ships_outside_playable_grid:
            with self.subTest(ship):
                self.assertFalse(board.ship_is_within_playable_grid(ship))

    def test_sufficient_remaining_ship_fields_to_mark_ship(self):
        parameters_vector = (
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 1), 3, Series.ROW),
                True,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(2)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 1), 3, Series.ROW),
                False,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (0) (2) (1) (2) ",
                Ship(Position(1, 1), 3, Series.ROW),
                False,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 1), 3, Series.COLUMN),
                True,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (2) (1) (2) (1) (2) ",
                Ship(Position(1, 1), 3, Series.COLUMN),
                False,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(0)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 1), 3, Series.COLUMN),
                False,
            ),
        )
        for board_repr, ship, expected_result in parameters_vector:
            with self.subTest():
                self.assertEqual(
                    expected_result,
                    parse_board(
                        board_repr
                    ).sufficient_remaining_ship_fields_to_mark_ship(ship),
                )

    def test_no_disallowed_overlapping_fields_for_ship(self):
        parameters_vector = (
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 2), 3, Series.ROW),
                True,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   x   .  ║(3)\n"
                "║  x   .   .   .   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 2), 3, Series.ROW),
                True,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   .   x   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 2), 3, Series.ROW),
                False,
            ),
            (
                "╔═════════════════════╗\n"
                "║  x   x   x   O   .  ║(3)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "║  x   x   O   x   x  ║(2)\n"
                "║  x   .   x   x   x  ║(1)\n"
                "║  x   x   x   x   x  ║(2)\n"
                "╚═════════════════════╝\n"
                "  (4) (1) (2) (1) (2) ",
                Ship(Position(1, 2), 3, Series.ROW),
                False,
            ),
        )
        for board_repr, ship, expected_result in parameters_vector:
            with self.subTest():
                self.assertEqual(
                    expected_result,
                    parse_board(board_repr).no_disallowed_overlapping_fields_for_ship(
                        ship
                    ),
                )

    @unittest.mock.patch.object(Board, "no_disallowed_overlapping_fields_for_ship")
    @unittest.mock.patch.object(Board, "sufficient_remaining_ship_fields_to_mark_ship")
    @unittest.mock.patch.object(Board, "ship_is_within_playable_grid")
    def test_can_fit_ship(
        self,
        mock_ship_is_within_playable_grid,
        mock_sufficient_remaining_ship_fields_to_mark_ship,
        mock_no_disallowed_overlapping_fields_for_ship,
    ):
        ship = unittest.mock.Mock(spec=Ship)
        mock_ship_is_within_playable_grid.return_value = True
        mock_sufficient_remaining_ship_fields_to_mark_ship.return_value = True
        mock_no_disallowed_overlapping_fields_for_ship.return_value = True
        self.assertTrue(self.sample_board.can_fit_ship(ship))
        random.choice(
            [
                mock_ship_is_within_playable_grid,
                mock_sufficient_remaining_ship_fields_to_mark_ship,
                mock_no_disallowed_overlapping_fields_for_ship,
            ]
        ).return_value = False
        self.assertFalse(self.sample_board.can_fit_ship(ship))

    def test_simulate_marking_of_ships(self):
        actual_board = parse_board(
            "╔═════════════════════╗\n"
            "║  x   x   x   x   .  ║(3)\n"
            "║  x   x   x   x   x  ║(0)\n"
            "║  x   x   O   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "╚═════════════════════╝\n"
            "  (4) (1) (2) (1) (2) "
        )
        ships = {
            Ship(Position(1, 1), 3, Series.ROW),
            Ship(Position(3, 5), 2, Series.COLUMN),
        }
        ships_orig = set(ships)
        actual_board.mark_ship_group(ships)
        expected_board = parse_board(
            "╔═════════════════════╗\n"
            "║  O   O   O   .   .  ║(0)\n"
            "║  .   .   .   .   .  ║(0)\n"
            "║  x   .   O   .   O  ║(1)\n"
            "║  .   .   .   .   O  ║(0)\n"
            "║  x   .   x   .   .  ║(2)\n"
            "╚═════════════════════╝\n"
            "  (3) (0) (1) (1) (0) "
        )
        self.assertEqual(actual_board, expected_board)
        self.assertEqual(ships, ships_orig)

        actual_board = parse_board(
            "╔═════════════════════╗\n"
            "║  x   x   x   x   .  ║(3)\n"
            "║  x   x   x   x   x  ║(0)\n"
            "║  x   x   O   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "╚═════════════════════╝\n"
            "  (4) (1) (2) (1) (2) "
        )
        ships = {
            Ship(Position(1, 1), 3, Series.ROW),
            Ship(Position(3, 5), 2, Series.COLUMN),
            Ship(Position(5, 1), 3, Series.ROW),
        }
        ships_orig = set(ships)
        with self.assertRaises(InvalidShipPlacementException):
            actual_board.mark_ship_group(ships)

    def test_find_definite_ship_fields_positions(self):
        board = parse_board(
            "╔═════════════════════╗\n"
            "║  x   x   x   .   .  ║(3)\n"
            "║  x   x   .   x   x  ║(0)\n"
            "║  x   x   O   x   .  ║(2)\n"
            "║  x   .   .   x   x  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "╚═════════════════════╝\n"
            "  (4) (1) (2) (1) (0) "
        )
        expected_result = {
            Position(1, 3),
            Position(5, 3),
            Position(1, 1),
            Position(1, 2),
            Position(3, 1),
            Position(4, 1),
            Position(5, 1),
            Position(3, 4),
        }
        self.assertEqual(expected_result, board.find_definite_ship_fields_positions())

    def test_get_possible_ships_occupying_positions(self):
        actual_board = parse_board(
            "╔═════════════════════╗\n"
            "║  x   x   x   x   .  ║(3)\n"
            "║  x   x   x   x   x  ║(0)\n"
            "║  x   x   O   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "╚═════════════════════╝\n"
            "  (4) (1) (2) (1) (2) "
        )
        positions = {Position(1, 3), Position(5, 1)}
        positions_orig = set(positions)
        ship_sizes = {3, 2, 1}
        ship_sizes_orig = set(ship_sizes)
        expected_ship_occupying_positions = {
            Position(1, 3): {
                Ship(Position(1, 1), 3, Series.ROW),
                Ship(Position(1, 2), 3, Series.ROW),
                Ship(Position(1, 2), 2, Series.ROW),
                Ship(Position(1, 3), 2, Series.ROW),
                Ship(Position(1, 3), 1, Series.ROW),
            },
            Position(5, 1): {
                Ship(Position(5, 1), 2, Series.ROW),
                Ship(Position(5, 1), 1, Series.ROW),
                Ship(Position(3, 1), 3, Series.COLUMN),
                Ship(Position(4, 1), 2, Series.COLUMN),
            },
        }
        self.assertEqual(
            expected_ship_occupying_positions,
            actual_board.get_possible_ships_occupying_positions(positions, ship_sizes),
        )
        self.assertEqual(positions, positions_orig)
        self.assertEqual(ship_sizes, ship_sizes_orig)

    def test_get_possible_ships_of_size(self):
        board = parse_board(
            "╔═════════════════════╗\n"
            "║  x   x   x   x   .  ║(3)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "║  x   x   O   x   x  ║(2)\n"
            "║  x   .   x   x   x  ║(1)\n"
            "║  x   x   x   x   x  ║(2)\n"
            "╚═════════════════════╝\n"
            "  (4) (1) (2) (1) (2) "
        )
        self.assertEqual(
            {
                Ship(Position(1, 1), 3, Series.ROW),
                Ship(Position(1, 2), 3, Series.ROW),
                Ship(Position(1, 1), 3, Series.COLUMN),
                Ship(Position(2, 1), 3, Series.COLUMN),
                Ship(Position(3, 1), 3, Series.COLUMN),
            },
            board.get_possible_ships_of_size(3),
        )
        self.assertEqual(
            {
                Ship(Position(1, 1), 2, Series.ROW),
                Ship(Position(1, 2), 2, Series.ROW),
                Ship(Position(1, 3), 2, Series.ROW),
                Ship(Position(5, 1), 2, Series.ROW),
                Ship(Position(5, 2), 2, Series.ROW),
                Ship(Position(5, 3), 2, Series.ROW),
                Ship(Position(5, 4), 2, Series.ROW),
                Ship(Position(1, 1), 2, Series.COLUMN),
                Ship(Position(2, 1), 2, Series.COLUMN),
                Ship(Position(3, 1), 2, Series.COLUMN),
                Ship(Position(4, 1), 2, Series.COLUMN),
                Ship(Position(2, 5), 2, Series.COLUMN),
                Ship(Position(3, 5), 2, Series.COLUMN),
                Ship(Position(4, 5), 2, Series.COLUMN),
            },
            board.get_possible_ships_of_size(2),
        )
        self.assertEqual(
            {
                Ship(Position(1, 1), 1, Series.ROW),
                Ship(Position(1, 2), 1, Series.ROW),
                Ship(Position(1, 3), 1, Series.ROW),
                Ship(Position(1, 4), 1, Series.ROW),
                Ship(Position(2, 1), 1, Series.ROW),
                Ship(Position(2, 5), 1, Series.ROW),
                Ship(Position(3, 1), 1, Series.ROW),
                Ship(Position(3, 5), 1, Series.ROW),
                Ship(Position(4, 1), 1, Series.ROW),
                Ship(Position(4, 5), 1, Series.ROW),
                Ship(Position(5, 1), 1, Series.ROW),
                Ship(Position(5, 2), 1, Series.ROW),
                Ship(Position(5, 3), 1, Series.ROW),
                Ship(Position(5, 4), 1, Series.ROW),
                Ship(Position(5, 5), 1, Series.ROW),
            },
            board.get_possible_ships_of_size(1),
        )

    def test_mark_ship_and_surrounding_sea(self):
        actual_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   .   x   x   x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   .   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   .   x   x   x   x   x  ║(1)\n"
            "║  x   x   x   x   x   x   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (4) (0) (0) (0) (0) "
        )
        actual_board.mark_ship_and_surrounding_sea(
            Ship(Position(5, 6), 4, Series.COLUMN)
        )
        expected_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   .   x   x   x   x   x   x   x  ║(2)\n"
            "║  x   .   x   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   .   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   .   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (0) (0) (0) (0) (0) (0) (0) (0) "
        )
        self.assertEqual(expected_board, actual_board)

        actual_board.mark_ship_and_surrounding_sea(Ship(Position(2, 1), 2, Series.ROW))
        expected_board = parse_board(
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   x   x   x   x   x   x   x  ║(0)\n"
            "║  O   O   .   x   x   x   x   x   x   x  ║(0)\n"
            "║  .   .   .   x   x   x   x   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   .   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   O   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   .   .   .   x   x   x  ║(0)\n"
            "║  x   x   x   x   x   x   x   x   x   x  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (0) (0) (0) (0) (0) (0) (0) (0) (0) (0) "
        )
        self.assertEqual(expected_board, actual_board)

    def test_is_overmarked(self):
        sample_board_repr = (
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   x   x   x   x   x   x   .   .   .  ║(1)\n"
            "║  .   .   O   .   .   .   .   .   .   .  ║(0)\n"
            "║  .   .   O   x   x   x   x   .   .   O  ║(3)\n"
            "║  .   .   O   .   .   .   .   .   .   .  ║(0)\n"
            "║  .   .   .   x   x   x   x   .   .   x  ║(4)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   .   x   x   .   .   .   .   O   O  ║(0)\n"
            "║  x   .   .   .   .   x   .   .   .   x  ║(1)\n"
            "║  O   .   O   O   O   O   .   O   O   .  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (1) (3) (3) (4) (1) (0) (0) (1) "
        )
        self.assertFalse(parse_board(sample_board_repr).is_overmarked())

        sample_board_repr = (
            "╔═════════════════════════════════════════╗\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   x   x   x   x   x   x   .   .   .  ║(1)\n"
            "║  .   .   O   .   .   .   .   .   .   .  ║(0)\n"
            "║  .   .   O   x   x   x   x   .   .   O  ║(3)\n"
            "║  .   .   O   .   .   .   .   .   .   .  ║(0)\n"
            "║  .   .   .   x   x   x   x   .   .   x  ║(4)\n"
            "║  .   .   .   .   .   .   .   .   .   .  ║(0)\n"
            "║  x   .   x   x   .   .   .   .   O   O  ║(0)\n"
            "║  x   .   .   .   .   x   .   .   .   x  ║(1)\n"
            "║  O   .   O   O   O   O   .   O   O   .  ║(0)\n"
            "╚═════════════════════════════════════════╝\n"
            "  (1) (1) (1) (3) (3) (5) (1) (0) (0) (1) "
        )
        self.assertTrue(parse_board(sample_board_repr).is_overmarked())
