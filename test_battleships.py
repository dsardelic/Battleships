from configparser import ConfigParser
from pathlib import Path
import random
import re
from unittest import TestCase, mock

import battleships as bs


class BattleshipsTest(TestCase):
    def setUp(self):
        random.seed()
        self.sample_config_file_path = (
            Path(__file__)
            .absolute()
            .parent.joinpath("test_data/Battleships_has_solutions.ini")
        )
        self.sample_config = ConfigParser()
        self.sample_config.read(self.sample_config_file_path)
        bs.FieldType = bs.get_redefined_fieldtypes(self.sample_config)
        sample_game_data = bs.parse_game_data_file(
            self.sample_config["GAMEDATA"]["FILEPATH"]
        )
        self.sample_exp_board = bs.Board.get_board_from_game_data(
            sample_game_data.playfield,
            sample_game_data.solution_pcs_in_rows,
            sample_game_data.solution_pcs_in_cols,
        )
        self.sample_exp_fleet = sample_game_data.fleet

    @staticmethod
    def parse_board(board_repr):
        playfield = []
        rem_pcs_in_rows = []
        rem_pcs_in_cols = []
        total_pcs_in_rows = []
        total_pcs_in_cols = []
        lines = board_repr.split("\n")
        lines_count = len(lines) - 1
        for row in range(1, lines_count):
            line = lines[row].strip()
            if row < lines_count - 3:
                playfield.append(
                    [bs.FieldType(token) for token in list(re.sub("[^.xO]", "", line))]
                )
                pcs_in_row, total_pcs_in_row = map(
                    int, re.findall(r"\((\d+)\)", line[line.index("║") + 1 :])
                )
                rem_pcs_in_rows.append(total_pcs_in_row - pcs_in_row)
                total_pcs_in_rows.append(total_pcs_in_row)
            elif row == lines_count - 2:
                pcs_in_cols = list(map(int, re.findall(r"\((\d+)\)", line.strip())))
            elif row == lines_count - 1:
                total_pcs_in_cols = list(
                    map(int, re.findall(r"\((\d+)\)", line.strip()))
                )
                rem_pcs_in_cols = [
                    total_pcs_in_cols[i] - pcs_in_cols[i]
                    for i in range(len(total_pcs_in_cols))
                ]
        board = bs.Board.get_board_from_game_data(
            playfield, rem_pcs_in_rows, rem_pcs_in_cols
        )
        board.total_pcs_in_rows = [0, *total_pcs_in_rows, 0]
        board.total_pcs_in_cols = [0, *total_pcs_in_cols, 0]
        return board

    def test_parse_board(self):
        self.assertEqual(
            self.sample_exp_board, self.parse_board(self.sample_exp_board.__repr__())
        )

    def test_board_init(self):
        size = random.randrange(8, 11)
        playfield = [
            [random.choice(list(bs.FieldType)) for _ in range(size)]
            for _ in range(size)
        ]
        rem_pcs_in_rows = [random.randrange(size - 5) for _ in range(size)]
        rem_pcs_in_cols = [random.randrange(size - 5) for _ in range(size)]
        board = bs.Board(playfield, rem_pcs_in_rows, rem_pcs_in_cols)
        self.assertEqual(board.size, size)
        self.assertEqual(board.playfield, playfield)
        self.assertEqual(board.rem_pcs_in_rows, rem_pcs_in_rows)
        self.assertEqual(board.rem_pcs_in_cols, rem_pcs_in_cols)
        self.assertFalse(board.playfield is playfield)
        self.assertFalse(board.rem_pcs_in_rows is rem_pcs_in_rows)
        self.assertFalse(board.rem_pcs_in_cols is rem_pcs_in_cols)
        self.assertEqual(board.total_pcs_in_rows, rem_pcs_in_rows)
        self.assertEqual(board.total_pcs_in_cols, rem_pcs_in_cols)
        self.assertFalse(board.total_pcs_in_rows is rem_pcs_in_rows)
        self.assertFalse(board.total_pcs_in_cols is rem_pcs_in_cols)

        total_pcs_in_rows = [x + random.randrange(5) for x in rem_pcs_in_rows]
        total_pcs_in_cols = [x + random.randrange(5) for x in rem_pcs_in_cols]
        board = bs.Board(
            playfield,
            rem_pcs_in_rows,
            rem_pcs_in_cols,
            total_pcs_in_rows,
            total_pcs_in_cols,
        )
        self.assertEqual(board.total_pcs_in_rows, total_pcs_in_rows)
        self.assertEqual(board.total_pcs_in_cols, total_pcs_in_cols)
        self.assertFalse(board.total_pcs_in_rows is total_pcs_in_rows)
        self.assertFalse(board.total_pcs_in_cols is total_pcs_in_cols)

    def test_board_repr(self):
        exp_repr = (
            "═════════════════════════════════════════\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(1)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(3)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(3)\n"
            " x   x   O   x   x   x   x   x   x   x   ║(1)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(1)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(2)\n"
            " x   x   .   x   .   x   x   .   x   x   ║(2)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)\n"
            " x   x   x   x   O   x   x   x   x   x   ║(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.assertEqual(self.sample_exp_board.repr(True), exp_repr)

        exp_repr = (
            "═════════════════════════════════════════\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(0)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(1)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(3)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(3)\n"
            " x   x   O   x   x   x   x   x   x   x   ║(0)(1)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(1)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(2)\n"
            " x   x   .   x   .   x   x   .   x   x   ║(0)(2)\n"
            " x   x   x   x   x   x   x   x   x   x   ║(0)(0)\n"
            " x   x   x   x   O   x   x   x   x   x   ║(0)(7)\n"
            "═════════════════════════════════════════\n"
            "(0) (0) (0) (0) (0) (0) (0) (0) (0) (0) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.assertEqual(self.sample_exp_board.__repr__(), exp_repr)

    def test_board_eq(self):
        playfield = [[bs.FieldType.UNKNOWN] * 12 for _ in range(12)]
        for i in range(12):
            playfield[i][0] = bs.FieldType.SEA
            playfield[0][i] = bs.FieldType.SEA
            playfield[11][i] = bs.FieldType.SEA
            playfield[i][11] = bs.FieldType.SEA
        playfield[5][3] = bs.FieldType.SHIP
        playfield[8][3] = bs.FieldType.SEA
        playfield[8][5] = bs.FieldType.SEA
        playfield[8][8] = bs.FieldType.SEA
        playfield[10][5] = bs.FieldType.SHIP
        board = bs.Board(
            playfield,
            [0, 0, 1, 3, 3, 1, 1, 2, 2, 0, 7, 0],
            [0, 1, 1, 4, 1, 6, 1, 0, 2, 2, 2, 0],
        )
        self.assertTrue(self.sample_exp_board.__eq__(board))
        self.assertFalse(self.sample_exp_board is board)

        board.playfield[1][1] = bs.FieldType.SEA
        self.assertFalse(self.sample_exp_board.__eq__(board))

        self.assertFalse(self.sample_exp_board.__eq__("board"))

    def test_board_get_copy(self):
        board = self.sample_exp_board.get_copy()
        self.assertEqual(self.sample_exp_board, board)
        self.assertFalse(self.sample_exp_board is board)

    def test_fleet_eq(self):
        fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 2, 2: 3, 1: 4})
        self.assertTrue(self.sample_exp_fleet.__eq__(fleet))
        self.assertFalse(self.sample_exp_fleet is fleet)

        fleet.ship_lengths[0] = 5
        self.assertFalse(self.sample_exp_fleet.__eq__(fleet))

    def test_fleet_get_copy(self):
        fleet = self.sample_exp_fleet.get_copy()
        self.assertEqual(self.sample_exp_fleet, fleet)
        self.assertFalse(self.sample_exp_fleet is fleet)

    def test_get_redefined_fieldtypes(self):
        FieldType = bs.get_redefined_fieldtypes(self.sample_config)
        self.assertEqual(FieldType.SEA.value, ".")
        self.assertEqual(FieldType.SHIP.value, "O")
        self.assertEqual(FieldType.UNKNOWN.value, "x")

    @mock.patch.object(bs.Path, "is_absolute")
    @mock.patch.object(bs.Path, "absolute")
    @mock.patch.object(bs.Path, "exists")
    def test_get_absolute_path(
        self, mock_path_exists, mock_path_absolute, mock_path_is_absolute
    ):
        abs_path = "/home/user/file.in"
        path = Path(abs_path)
        mock_path_is_absolute.return_value = True
        mock_path_exists.return_value = True
        self.assertEqual(bs.get_absolute_path(abs_path), path)
        mock_path_is_absolute.return_value = True
        mock_path_exists.return_value = False
        self.assertIsNone(bs.get_absolute_path(abs_path))
        mock_path_is_absolute.return_value = False
        rel_path = "rel_path/file.in"
        mock_path_absolute.return_value = Path("/Battleships/battleships.py")
        mock_path_exists.return_value = True
        self.assertEqual(
            bs.get_absolute_path(rel_path), Path("/Battleships/rel_path/file.in")
        )
        mock_path_exists.return_value = False
        self.assertIsNone(bs.get_absolute_path(rel_path))

    @mock.patch("battleships.print")
    @mock.patch("battleships.sys")
    def test_parse_game_data_file(self, mocked_sys, mocked_print):
        exp_playfield = [[bs.FieldType.UNKNOWN] * 10 for _ in range(10)]
        exp_playfield[4][2] = bs.FieldType.SHIP
        exp_playfield[7][2] = bs.FieldType.SEA
        exp_playfield[7][4] = bs.FieldType.SEA
        exp_playfield[7][7] = bs.FieldType.SEA
        exp_playfield[9][4] = bs.FieldType.SHIP
        game_data = bs.parse_game_data_file(self.sample_config["GAMEDATA"]["FILEPATH"])
        self.assertEqual(game_data.playfield, exp_playfield)
        self.assertEqual(game_data.solution_pcs_in_rows, [0, 1, 3, 3, 1, 1, 2, 2, 0, 7])
        self.assertEqual(game_data.solution_pcs_in_cols, [1, 1, 4, 1, 6, 1, 0, 2, 2, 2])
        self.assertEqual(
            game_data.fleet, bs.Fleet([4, 3, 2, 1], {4: 1, 3: 2, 2: 3, 1: 4})
        )
        input_file_path = None
        bs.parse_game_data_file(input_file_path)
        mocked_print.assert_called_once()
        mocked_print.assert_called_with(
            "Invalid game input file path", file=mocked_sys.stderr
        )
        mocked_sys.exit.assert_called_once()
        mocked_sys.exit.assert_called_with(-1)

    def test_get_board_from_input_data(self):
        playfield = [[bs.FieldType.UNKNOWN] * 10 for _ in range(10)]
        playfield[4][2] = bs.FieldType.SHIP
        playfield[7][2] = bs.FieldType.SEA
        playfield[7][4] = bs.FieldType.SEA
        playfield[7][7] = bs.FieldType.SEA
        playfield[9][4] = bs.FieldType.SHIP
        rem_pcs_in_rows = [0, 1, 3, 3, 1, 1, 2, 2, 0, 7]
        rem_pcs_in_cols = [1, 1, 4, 1, 6, 1, 0, 2, 2, 2]

        exp_playfield = [[bs.FieldType.UNKNOWN] * 12 for _ in range(12)]
        for i in range(12):
            exp_playfield[i][0] = bs.FieldType.SEA
            exp_playfield[0][i] = bs.FieldType.SEA
            exp_playfield[11][i] = bs.FieldType.SEA
            exp_playfield[i][11] = bs.FieldType.SEA
        exp_playfield[5][3] = bs.FieldType.SHIP
        exp_playfield[8][3] = bs.FieldType.SEA
        exp_playfield[8][5] = bs.FieldType.SEA
        exp_playfield[8][8] = bs.FieldType.SEA
        exp_playfield[10][5] = bs.FieldType.SHIP
        exp_rem_pcs_in_rows = [0, 0, 1, 3, 3, 1, 1, 2, 2, 0, 7, 0]
        exp_rem_pcs_in_cols = [0, 1, 1, 4, 1, 6, 1, 0, 2, 2, 2, 0]

        self.assertEqual(
            bs.Board.get_board_from_game_data(
                playfield, rem_pcs_in_rows, rem_pcs_in_cols
            ),
            bs.Board(exp_playfield, exp_rem_pcs_in_rows, exp_rem_pcs_in_cols),
        )

    def test_get_ship_pcs_positions(self):
        act_board = self.sample_exp_board.get_copy()
        self.assertEqual(bs.get_ship_pcs_positions(act_board), [(5, 3), (10, 5)])
        self.assertEqual(act_board, self.sample_exp_board)

    def test_mark_uncovered_sea_positions(self):
        act_board = self.sample_exp_board.get_copy()
        act_ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        exp_ship_pcs_positions = [*act_ship_pcs_positions]
        bs.mark_uncovered_sea_positions(act_board, act_ship_pcs_positions)
        exp_board_repr = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " x   x   x   x   x   x   .   x   x   x   ║(0)(1)\n"
            " x   x   x   x   x   x   .   x   x   x   ║(0)(3)\n"
            " x   .   x   .   x   x   .   x   x   x   ║(0)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(0)(1)\n"
            " x   .   x   .   x   x   .   x   x   x   ║(0)(1)\n"
            " x   x   x   x   x   x   .   x   x   x   ║(0)(2)\n"
            " x   x   .   x   .   x   .   .   x   x   ║(0)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " x   x   x   x   O   x   .   x   x   x   ║(0)(7)\n"
            "═════════════════════════════════════════\n"
            "(0) (0) (0) (0) (0) (0) (0) (0) (0) (0) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.assertEqual(act_board, self.parse_board(exp_board_repr))
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)

    def test_ship_cannot_exceed_rem_pcs_in_rows(self):
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(3, 7, 4, bs.Direction.RIGHT), False),
            (bs.Ship(1, 5, 1, bs.Direction.RIGHT), False),
            (bs.Ship(10, 7, 4, bs.Direction.RIGHT), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_ship_cannot_exceed_rem_pcs_in_cols(self):
        self.sample_exp_board.rem_pcs_in_rows[9] = 1
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(9, 1, 2, bs.Direction.DOWN), False),
            (bs.Ship(9, 7, 2, bs.Direction.DOWN), False),
            (bs.Ship(9, 10, 2, bs.Direction.DOWN), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_ship_cannot_overflow_row(self):
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(3, 9, 3, bs.Direction.RIGHT), False),
            (bs.Ship(3, 8, 3, bs.Direction.RIGHT), True),
            (bs.Ship(10, 10, 1, bs.Direction.RIGHT), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_ship_cannot_overflow_column(self):
        self.sample_exp_board.playfield[8][8] = bs.FieldType.UNKNOWN
        self.sample_exp_board.rem_pcs_in_rows[9] = 1
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(10, 10, 2, bs.Direction.DOWN), False),
            (bs.Ship(9, 10, 2, bs.Direction.DOWN), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_all_ship_pcs_in_rows_must_initially_be_unknown(self):
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(10, 2, 4, bs.Direction.RIGHT), False),
            (bs.Ship(10, 1, 3, bs.Direction.RIGHT), True),
            (bs.Ship(8, 3, 1, bs.Direction.RIGHT), False),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_all_ship_pcs_in_columns_must_initially_be_unknown(self):
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(7, 8, 2, bs.Direction.DOWN), False),
            (bs.Ship(6, 8, 2, bs.Direction.DOWN), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_ship_must_not_touch_another_ship(self):
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(6, 4, 1, bs.Direction.RIGHT), False),
            (bs.Ship(6, 3, 1, bs.Direction.RIGHT), False),
            (bs.Ship(6, 2, 1, bs.Direction.RIGHT), False),
            (bs.Ship(10, 2, 3, bs.Direction.RIGHT), False),
            (bs.Ship(4, 1, 2, bs.Direction.RIGHT), False),
            (bs.Ship(4, 1, 3, bs.Direction.RIGHT), False),
            (bs.Ship(4, 4, 3, bs.Direction.RIGHT), False),
            (bs.Ship(10, 6, 1, bs.Direction.RIGHT), False),
            (bs.Ship(10, 8, 3, bs.Direction.RIGHT), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

        self.sample_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        self.sample_exp_board.playfield[4][9] = bs.FieldType.SHIP
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (bs.Ship(5, 10, 2, bs.Direction.DOWN), False),
            (bs.Ship(5, 9, 2, bs.Direction.DOWN), False),
            (bs.Ship(5, 8, 2, bs.Direction.DOWN), False),
            (bs.Ship(4, 8, 2, bs.Direction.DOWN), False),
            (bs.Ship(2, 8, 2, bs.Direction.DOWN), False),
            (bs.Ship(2, 9, 2, bs.Direction.DOWN), False),
            (bs.Ship(2, 10, 2, bs.Direction.DOWN), False),
            (bs.Ship(4, 10, 2, bs.Direction.DOWN), False),
            (bs.Ship(2, 5, 3, bs.Direction.DOWN), True),
        )
        for ship, exp_value in test_data:
            with self.subTest(ship):
                self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), exp_value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_reduce_rem_pcs_and_mark_sea_in_filled_rows(self):
        self.sample_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        self.sample_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        self.sample_exp_board.rem_pcs_in_cols[8] = 1
        act_board = self.sample_exp_board.get_copy()
        bs.reduce_rem_pcs_and_mark_sea(act_board, bs.Ship(4, 8, 3, bs.Direction.RIGHT))
        self.sample_exp_board.rem_pcs_in_rows[4] = 0
        self.sample_exp_board.rem_pcs_in_cols[8] = 0
        self.sample_exp_board.rem_pcs_in_cols[9] = 1
        self.sample_exp_board.rem_pcs_in_cols[10] = 1
        for i in range(1, 11):
            self.sample_exp_board.playfield[4][i] = bs.FieldType.SEA
            self.sample_exp_board.playfield[i][8] = bs.FieldType.SEA
        self.assertEqual(act_board, self.sample_exp_board)

    def test_reduce_rem_pcs_and_mark_sea_in_filled_columns(self):
        self.sample_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        self.sample_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = self.sample_exp_board.get_copy()
        bs.reduce_rem_pcs_and_mark_sea(act_board, bs.Ship(2, 8, 2, bs.Direction.DOWN))
        self.sample_exp_board.rem_pcs_in_cols[8] = 0
        self.sample_exp_board.rem_pcs_in_rows[2] = 0
        self.sample_exp_board.rem_pcs_in_rows[3] = 2
        for i in range(1, 11):
            self.sample_exp_board.playfield[2][i] = bs.FieldType.SEA
            self.sample_exp_board.playfield[i][8] = bs.FieldType.SEA
        self.assertEqual(act_board, self.sample_exp_board)

    def test_mark_ship_in_row(self):
        ship = bs.Ship(10, 2, 4, bs.Direction.RIGHT)
        act_board = self.sample_exp_board.get_copy()
        bs.mark_ship(act_board, ship)
        for i in range(2, 6):
            self.sample_exp_board.playfield[10][i] = bs.FieldType.SHIP
        for i in range(1, 7):
            self.sample_exp_board.playfield[9][i] = bs.FieldType.SEA
            self.sample_exp_board.playfield[11][i] = bs.FieldType.SEA
            self.sample_exp_board.playfield[10][1] = bs.FieldType.SEA
            self.sample_exp_board.playfield[10][6] = bs.FieldType.SEA
        self.assertEqual(act_board, self.sample_exp_board)

    def test_mark_ship_of_size_one(self):
        ship = bs.Ship(2, 1, 1, bs.Direction.RIGHT)
        act_board = self.sample_exp_board.get_copy()
        bs.mark_ship(act_board, ship)
        self.sample_exp_board.playfield[2][1] = bs.FieldType.SHIP
        for i in range(3):
            self.sample_exp_board.playfield[1][i] = bs.FieldType.SEA
            self.sample_exp_board.playfield[3][i] = bs.FieldType.SEA
            self.sample_exp_board.playfield[2][0] = bs.FieldType.SEA
            self.sample_exp_board.playfield[2][2] = bs.FieldType.SEA
        self.assertEqual(act_board, self.sample_exp_board)

    def test_mark_ship_in_column(self):
        ship = bs.Ship(2, 3, 4, bs.Direction.DOWN)
        act_board = self.sample_exp_board.get_copy()
        bs.mark_ship(act_board, ship)
        for i in range(2, 6):
            self.sample_exp_board.playfield[i][3] = bs.FieldType.SHIP
        for i in range(1, 7):
            self.sample_exp_board.playfield[i][2] = bs.FieldType.SEA
        for i in range(1, 7):
            self.sample_exp_board.playfield[i][4] = bs.FieldType.SEA
            self.sample_exp_board.playfield[1][3] = bs.FieldType.SEA
            self.sample_exp_board.playfield[6][3] = bs.FieldType.SEA
        self.assertEqual(act_board, self.sample_exp_board)

    def test_mark_ships_passes(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        for x, y in ship_pcs_positions:
            self.sample_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(self.sample_exp_board, ship_pcs_positions)
        act_board = self.sample_exp_board.get_copy()
        act_fleet = self.sample_exp_fleet.get_copy()
        self.assertTrue(
            bs.mark_ships(
                act_board,
                act_fleet,
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(2, 10, 1, bs.Direction.RIGHT),
                    bs.Ship(3, 3, 3, bs.Direction.DOWN),
                ],
            )
        )
        exp_board_repr = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   .   .   .   .   .   O   ║(1)(1)\n"
            " x   .   O   .   x   x   .   x   .   .   ║(1)(3)\n"
            " x   .   O   .   x   x   .   x   x   x   ║(1)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " x   .   .   .   x   x   .   x   x   x   ║(0)(1)\n"
            " x   .   .   .   x   x   .   x   x   x   ║(0)(2)\n"
            " x   .   .   .   .   x   .   .   x   x   ║(0)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   O   O   O   O   .   .   x   x   x   ║(4)(7)\n"
            "═════════════════════════════════════════\n"
            "(0) (1) (4) (1) (1) (0) (0) (0) (0) (1) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.assertEqual(act_board, self.parse_board(exp_board_repr))
        self.assertEqual(act_fleet, bs.Fleet([4, 3, 2, 1], {4: 0, 3: 1, 2: 3, 1: 3}))

    def test_mark_ships_fails_when_ship_pcs_exceeded(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        for x, y in ship_pcs_positions:
            self.sample_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(self.sample_exp_board, ship_pcs_positions)
        self.assertFalse(
            bs.mark_ships(
                self.sample_exp_board,
                self.sample_exp_fleet,
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(2, 10, 1, bs.Direction.RIGHT),
                    bs.Ship(2, 3, 3, bs.Direction.DOWN),
                ],
            )
        )

    def test_mark_ships_fails_when_ship_pcs_touch(self):
        ship_pcs_positions = [(10, 5)]
        for x, y in ship_pcs_positions:
            self.sample_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(self.sample_exp_board, ship_pcs_positions)
        self.assertFalse(
            bs.mark_ships(
                self.sample_exp_board,
                self.sample_exp_fleet,
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(2, 10, 1, bs.Direction.RIGHT),
                    bs.Ship(2, 3, 3, bs.Direction.DOWN),
                ],
            )
        )

    def test_get_ships_for_ship_piece_position(self):
        bs.mark_uncovered_sea_positions(self.sample_exp_board, [])
        self.sample_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (
                (5, 3, 4),
                [
                    bs.Ship(2, 3, 4, bs.Direction.DOWN),
                    bs.Ship(3, 3, 4, bs.Direction.DOWN),
                    bs.Ship(4, 3, 4, bs.Direction.DOWN),
                ],
            ),
            (
                (5, 3, 3),
                [
                    bs.Ship(3, 3, 3, bs.Direction.DOWN),
                    bs.Ship(4, 3, 3, bs.Direction.DOWN),
                    bs.Ship(5, 3, 3, bs.Direction.DOWN),
                ],
            ),
            (
                (5, 3, 2),
                [
                    bs.Ship(4, 3, 2, bs.Direction.DOWN),
                    bs.Ship(5, 3, 2, bs.Direction.DOWN),
                ],
            ),
            ((5, 3, 1), [bs.Ship(5, 3, 1, bs.Direction.RIGHT)]),
        )
        for params, value in test_data:
            with self.subTest(params):
                self.assertEqual(bs.get_field_ships(act_board, *params), value)
                self.assertEqual(act_board, self.sample_exp_board)

        self.sample_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (
                (10, 5, 4),
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(10, 3, 4, bs.Direction.RIGHT),
                ],
            ),
            (
                (10, 5, 3),
                [
                    bs.Ship(10, 3, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 4, 3, bs.Direction.RIGHT),
                ],
            ),
            (
                (10, 5, 2),
                [
                    bs.Ship(10, 4, 2, bs.Direction.RIGHT),
                    bs.Ship(10, 5, 2, bs.Direction.RIGHT),
                ],
            ),
            ((10, 5, 1), [bs.Ship(10, 5, 1, bs.Direction.RIGHT)]),
        )
        for params, value in test_data:
            with self.subTest(params):
                self.assertEqual(bs.get_field_ships(act_board, *params), value)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_get_ships_for_ship_pcs_positions(self):
        exp_ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        act_ship_positions = [*exp_ship_pcs_positions]
        bs.mark_uncovered_sea_positions(self.sample_exp_board, [])
        self.sample_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        self.sample_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = self.sample_exp_board.get_copy()
        exp_fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 2, 2: 0, 1: 4})
        act_fleet = exp_fleet.get_copy()
        self.assertEqual(
            bs.get_fields_ships_mappings(act_board, act_fleet, act_ship_positions),
            {
                (5, 3): [
                    bs.Ship(2, 3, 4, bs.Direction.DOWN),
                    bs.Ship(3, 3, 4, bs.Direction.DOWN),
                    bs.Ship(4, 3, 4, bs.Direction.DOWN),
                    bs.Ship(3, 3, 3, bs.Direction.DOWN),
                    bs.Ship(4, 3, 3, bs.Direction.DOWN),
                    bs.Ship(5, 3, 3, bs.Direction.DOWN),
                    bs.Ship(5, 3, 1, bs.Direction.RIGHT),
                ],
                (10, 5): [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(10, 3, 4, bs.Direction.RIGHT),
                    bs.Ship(10, 3, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 4, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 5, 1, bs.Direction.RIGHT),
                ],
            },
        )
        self.assertEqual(act_board, self.sample_exp_board)
        self.assertEqual(act_fleet, exp_fleet)
        self.assertEqual(act_ship_positions, exp_ship_pcs_positions)

    def test_reduce_ships_for_ship_pcs_positions_without_delete(self):
        exp_ship_pcs_positions = [(5, 3), (5, 5)]
        act_ship_pcs_positions = [*exp_ship_pcs_positions]
        ship = bs.Ship(5, 3, 3, bs.Direction.RIGHT)
        act_ships_for_ship_pcs_positions = {
            (5, 3): [
                bs.Ship(*ship),
                bs.Ship(5, 3, 2, bs.Direction.RIGHT),
                bs.Ship(5, 3, 1, bs.Direction.RIGHT),
            ],
            (5, 5): [
                bs.Ship(*ship),
                bs.Ship(5, 4, 2, bs.Direction.RIGHT),
                bs.Ship(5, 5, 1, bs.Direction.RIGHT),
            ],
        }
        exp_ships_for_ship_pcs_positions = {
            (5, 3): [
                bs.Ship(5, 3, 2, bs.Direction.RIGHT),
                bs.Ship(5, 3, 1, bs.Direction.RIGHT),
            ],
            (5, 5): [
                bs.Ship(5, 4, 2, bs.Direction.RIGHT),
                bs.Ship(5, 5, 1, bs.Direction.RIGHT),
            ],
        }
        bs.remove_ship_from_mappings(
            act_ship_pcs_positions, act_ships_for_ship_pcs_positions, ship
        )
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)
        self.assertEqual(
            act_ships_for_ship_pcs_positions, exp_ships_for_ship_pcs_positions
        )

    def test_reduce_ships_for_ship_pcs_positions_with_delete(self):
        exp_ship_pcs_positions = [(5, 3), (5, 6)]
        act_ship_pcs_positions = [*exp_ship_pcs_positions]
        ship = bs.Ship(5, 3, 4, bs.Direction.RIGHT)
        act_ships_for_ship_pcs_positions = {
            (5, 3): [bs.Ship(*ship), bs.Ship(5, 3, 2, bs.Direction.RIGHT)],
            (5, 6): [bs.Ship(*ship)],
        }
        exp_ships_for_ship_pcs_positions = {
            (5, 3): [bs.Ship(5, 3, 2, bs.Direction.RIGHT)]
        }
        bs.remove_ship_from_mappings(
            act_ship_pcs_positions, act_ships_for_ship_pcs_positions, ship
        )
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)
        self.assertEqual(
            act_ships_for_ship_pcs_positions, exp_ships_for_ship_pcs_positions
        )

    def test_mark_uncovered_ships(self):
        exp_ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        for x, y in exp_ship_pcs_positions:
            self.sample_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        act_ship_pcs_positions = [*exp_ship_pcs_positions]
        act_ships_for_ship_pcs_positions = {
            (5, 3): [
                bs.Ship(3, 3, 3, bs.Direction.DOWN),
                bs.Ship(4, 3, 3, bs.Direction.DOWN),
            ],
            (10, 5): [bs.Ship(10, 3, 4, bs.Direction.RIGHT)],
        }
        act_board = self.sample_exp_board.get_copy()
        act_fleet = self.sample_exp_fleet.get_copy()
        bs.mark_uncovered_ships(
            act_board,
            act_fleet,
            act_ship_pcs_positions,
            act_ships_for_ship_pcs_positions,
        )
        exp_board_repr = (
            "═════════════════════════════════════════\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(0)\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(1)\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(3)\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(3)\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(1)\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(1)\n"
            " x   x   x   .   x   .   x   x   x   x   ║(0)(2)\n"
            " x   x   .   .   .   .   x   .   x   x   ║(0)(2)\n"
            " x   .   .   .   .   .   .   x   x   x   ║(0)(0)\n"
            " x   .   O   O   O   O   .   x   x   x   ║(4)(7)\n"
            "═════════════════════════════════════════\n"
            "(0) (0) (1) (1) (1) (1) (0) (0) (0) (0) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.sample_exp_fleet.subfleet_sizes[4] = 0
        self.assertEqual(act_board, self.parse_board(exp_board_repr))
        self.assertEqual(act_fleet, self.sample_exp_fleet)
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)
        self.assertEqual(
            act_ships_for_ship_pcs_positions,
            {
                (5, 3): [
                    bs.Ship(3, 3, 3, bs.Direction.DOWN),
                    bs.Ship(4, 3, 3, bs.Direction.DOWN),
                ]
            },
        )

    def test_get_ships_of_length(self):
        bs.mark_uncovered_sea_positions(
            self.sample_exp_board, bs.get_ship_pcs_positions(self.sample_exp_board)
        )
        self.sample_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        self.sample_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = self.sample_exp_board.get_copy()
        test_data = (
            (
                4,
                [
                    bs.Ship(2, 3, 4, bs.Direction.DOWN),
                    bs.Ship(3, 3, 4, bs.Direction.DOWN),
                    bs.Ship(4, 3, 4, bs.Direction.DOWN),
                    bs.Ship(10, 1, 4, bs.Direction.RIGHT),
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(10, 3, 4, bs.Direction.RIGHT),
                ],
            ),
            (
                3,
                [
                    bs.Ship(2, 3, 3, bs.Direction.DOWN),
                    bs.Ship(2, 5, 3, bs.Direction.DOWN),
                    bs.Ship(3, 1, 3, bs.Direction.RIGHT),
                    bs.Ship(3, 2, 3, bs.Direction.RIGHT),
                    bs.Ship(3, 3, 3, bs.Direction.RIGHT),
                    bs.Ship(3, 3, 3, bs.Direction.DOWN),
                    bs.Ship(3, 4, 3, bs.Direction.RIGHT),
                    bs.Ship(3, 8, 3, bs.Direction.RIGHT),
                    bs.Ship(4, 3, 3, bs.Direction.DOWN),
                    bs.Ship(4, 8, 3, bs.Direction.RIGHT),
                    bs.Ship(5, 3, 3, bs.Direction.DOWN),
                    bs.Ship(10, 1, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 2, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 3, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 4, 3, bs.Direction.RIGHT),
                    bs.Ship(10, 8, 3, bs.Direction.RIGHT),
                ],
            ),
        )
        for ship_length, ships in test_data:
            with self.subTest(ship_length):
                self.assertEqual(bs.get_ships_of_length(act_board, ship_length), ships)
                self.assertEqual(act_board, self.sample_exp_board)

    def test_find_and_add_solutions_without_some_ship_types(self):
        act_board_repr = (
            "═════════════════════\n"
            " x   x   x   x   x   ║(0)(0)\n"
            " x   x   x   x   x   ║(0)(4)\n"
            " x   x   x   x   x   ║(0)(0)\n"
            " x   x   x   x   x   ║(0)(1)\n"
            " x   x   x   x   x   ║(0)(1)\n"
            "═════════════════════\n"
            "(0) (0) (0) (0) (0) \n"
            "(1) (1) (1) (1) (2) \n"
        )
        act_board = self.parse_board(act_board_repr)
        exp_board = act_board.get_copy()
        solution_board_repr = (
            "═════════════════════\n"
            " .   .   .   .   .   ║(0)(0)\n"
            " O   O   O   O   .   ║(4)(4)\n"
            " .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   ║(1)(1)\n"
            " .   .   .   .   O   ║(1)(1)\n"
            "═════════════════════\n"
            "(1) (1) (1) (1) (2) \n"
            "(1) (1) (1) (1) (2) \n"
        )
        act_fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 0, 2: 1, 1: 0})
        exp_fleet = act_fleet.get_copy()
        act_solutions = []
        bs.find_solutions_for_subfleet(act_board, act_fleet, 0, act_solutions)
        self.assertEqual(act_board, exp_board)
        self.assertEqual(act_fleet, exp_fleet)
        self.assertEqual(act_solutions, [self.parse_board(solution_board_repr)])

    def test_find_and_add_solutions_multiple_ship_positions(self):
        act_board_repr = (
            "═════════════════════════════\n"
            " .   .   x   x   x   x   x   ║(0)(1)\n"
            " .   x   x   x   x   x   x   ║(0)(1)\n"
            " .   x   x   x   x   x   x   ║(0)(2)\n"
            " .   x   x   x   x   x   x   ║(0)(2)\n"
            " .   x   x   x   x   x   x   ║(0)(2)\n"
            " .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   x   x   x   x   x   x   ║(0)(4)\n"
            "═════════════════════════════\n"
            "(0) (0) (0) (0) (0) (0) (0) \n"
            "(0) (5) (1) (1) (1) (1) (3) \n"
        )
        act_board = self.parse_board(act_board_repr)
        exp_board = act_board.get_copy()
        solution_board_repr = (
            "═════════════════════════════\n"
            " .   .   .   O   .   .   .   ║(1)(1)\n"
            " .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   .   .   O   ║(2)(2)\n"
            " .   O   .   .   .   .   O   ║(2)(2)\n"
            " .   O   .   .   .   .   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   O   O   .   O   O   .   ║(4)(4)\n"
            "═════════════════════════════\n"
            "(0) (5) (1) (1) (1) (1) (3) \n"
            "(0) (5) (1) (1) (1) (1) (3) \n"
        )
        act_fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 1, 2: 2, 1: 1})
        exp_fleet = act_fleet.get_copy()
        act_solutions = []
        bs.find_solutions_for_subfleet(act_board, act_fleet, 0, act_solutions)
        self.assertEqual(act_board, exp_board)
        self.assertEqual(act_fleet, exp_fleet)
        self.assertEqual(act_solutions, [self.parse_board(solution_board_repr)])

    def test_get_solution_boards_without_ships(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        for x, y in ship_pcs_positions:
            self.sample_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(self.sample_exp_board, ship_pcs_positions)
        act_board = self.sample_exp_board.get_copy()
        act_fleet = self.sample_exp_fleet.get_copy()
        act_ships_for_ship_pcs_positions = {}
        act_solutions = bs.get_solutions_for_mappings(
            act_board, act_fleet, act_ships_for_ship_pcs_positions
        )
        solution1 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " O   .   O   .   O   .   .   .   .   .   ║(3)(3)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   O   .   O   O   O   .   O   O   O   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution2 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " O   .   O   .   O   .   .   .   .   .   ║(3)(3)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   O   .   O   O   O   .   O   O   O   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution3 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution4 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution5 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   O   .   O   .   .   .   .   .   ║(3)(3)\n"
            " .   .   .   .   O   .   .   O   O   .   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n"
            " O   .   .   .   .   .   .   .   .   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   O   O   O   O   .   O   O   O   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.assertEqual(
            act_solutions,
            [
                self.parse_board(solution1),
                self.parse_board(solution2),
                self.parse_board(solution3),
                self.parse_board(solution4),
                self.parse_board(solution5),
            ],
        )
        self.assertEqual(act_board, self.sample_exp_board)
        self.assertEqual(act_fleet, self.sample_exp_fleet)
        self.assertEqual(act_ships_for_ship_pcs_positions, {})

    def test_get_solution_boards_with_ships(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(self.sample_exp_board)
        for x, y in ship_pcs_positions:
            self.sample_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(self.sample_exp_board, ship_pcs_positions)
        act_board = self.sample_exp_board.get_copy()
        act_fleet = self.sample_exp_fleet.get_copy()
        act_ships_for_ship_pcs_positions = bs.get_fields_ships_mappings(
            self.sample_exp_board, self.sample_exp_fleet, ship_pcs_positions
        )
        exp_ships_for_ship_pcs_positions = {**act_ships_for_ship_pcs_positions}
        act_solutions = bs.get_solutions_for_mappings(
            act_board, act_fleet, act_ships_for_ship_pcs_positions
        )
        solution1 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution2 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution3 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   O   .   O   .   .   .   .   .   ║(3)(3)\n"
            " .   .   .   .   O   .   .   O   O   .   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n"
            " O   .   .   .   .   .   .   .   .   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   O   O   O   O   .   O   O   O   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        self.assertEqual(
            act_solutions,
            [
                self.parse_board(solution1),
                self.parse_board(solution2),
                self.parse_board(solution3),
            ],
        )
        self.assertEqual(act_board, self.sample_exp_board)
        self.assertEqual(act_fleet, self.sample_exp_fleet)
        self.assertEqual(
            act_ships_for_ship_pcs_positions, exp_ships_for_ship_pcs_positions
        )

    def test_get_solutions_when_has_solutions(self):
        solution1 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution2 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n"
            " .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        solution3 = (
            "═════════════════════════════════════════\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   O   O   .   O   .   .   .   .   .   ║(3)(3)\n"
            " .   .   .   .   O   .   .   O   O   .   ║(3)(3)\n"
            " .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n"
            " .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n"
            " .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n"
            " O   .   .   .   .   .   .   .   .   O   ║(2)(2)\n"
            " .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n"
            " .   .   O   O   O   O   .   O   O   O   ║(7)(7)\n"
            "═════════════════════════════════════════\n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
            "(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n"
        )
        bs.CONFIG_FILE_PATH = self.sample_config_file_path
        self.assertEqual(
            bs.get_solutions(),
            [
                self.parse_board(solution1),
                self.parse_board(solution2),
                self.parse_board(solution3),
            ],
        )

    def test_get_solutions_when_no_solutions(self):
        bs.CONFIG_FILE_PATH = (
            Path(__file__)
            .absolute()
            .parent.joinpath("test_data/Battleships_has_no_solutions.ini")
        )
        self.assertEqual(bs.get_solutions(), [])
