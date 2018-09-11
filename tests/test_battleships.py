import os
import random
import re
import unittest

from battleships import battleships as bs


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAMPLE_CONFIG_FILE_PATH = os.path.join(
    BASE_DIR, 'tests/sample_configs/Battleships1.ini'
)
SAMPLE_CONFIG_FILE_PATH2 = os.path.join(
    BASE_DIR, 'tests/sample_configs/Battleships2.ini'
)


class BattleshipsTest(unittest.TestCase):

    def setUp(self):
        global g_exp_board
        global g_exp_fleet
        global config
        random.seed()
        config = bs.parse_config(SAMPLE_CONFIG_FILE_PATH)
        bs.FieldType = bs.get_redefined_FieldType(config)
        sample_input_data = bs.parse_game_data_file(
            config["GAMEDATA"]["FILEPATH"]
        )
        g_exp_board = bs.get_board_from_input_data(*sample_input_data[0:4])
        g_exp_fleet = sample_input_data[4]
        unittest.TestCase.setUp(self)

    def parse_board(self, board_repr):
        playfield, rem_pcs_in_rows, rem_pcs_in_cols, total_pcs_in_rows, \
            total_pcs_in_cols = [], [], [], [], []
        lines = board_repr.split('\n')
        lines_count = len(lines) - 1
        for row in range(1, lines_count):
            line = lines[row].strip()
            if row < lines_count - 3:
                playfield.append(
                    [
                        bs.FieldType(token)
                        for token in list(re.sub('[^.xO]', '', line))
                    ]
                )
                pcs_in_row, total_pcs_in_row = map(
                    int,
                    re.findall('\((\d+)\)', line[line.index('║') + 1:])
                )
                rem_pcs_in_rows.append(total_pcs_in_row - pcs_in_row)
                total_pcs_in_rows.append(total_pcs_in_row)
            elif row == lines_count - 2:
                pcs_in_cols = list(
                    map(int, re.findall('\((\d+)\)', line.strip()))
                )
            elif row == lines_count - 1:
                total_pcs_in_cols = list(
                    map(
                        int,
                        re.findall('\((\d+)\)', line.strip())
                    )
                )
                rem_pcs_in_cols = [
                    total_pcs_in_cols[i] - pcs_in_cols[i]
                    for i in range(len(total_pcs_in_cols))
                ]
        board = bs.get_board_from_input_data(
            lines_count - 4,
            playfield,
            rem_pcs_in_rows,
            rem_pcs_in_cols
        )
        board.total_pcs_in_rows = [0, *total_pcs_in_rows, 0]
        board.total_pcs_in_cols = [0, *total_pcs_in_cols, 0]
        return board

    def test_parse_board(self):
        self.assertEqual(g_exp_board, self.parse_board(g_exp_board.__repr__()))

    def test_direction_repr(self):
        self.assertEqual(bs.Direction.DOWN.__repr__(), '<Direction.DOWN>')

    def test_board_init(self):
        size = random.randrange(8, 11)
        playfield = [
            [random.choice(list(bs.FieldType)) for _ in range(size)]
            for _ in range(size)
        ]
        rem_pcs_in_rows = [random.randrange(size - 5) for _ in range(size)]
        rem_pcs_in_cols = [random.randrange(size - 5) for _ in range(size)]
        board = bs.Board(size, playfield, rem_pcs_in_rows, rem_pcs_in_cols)
        self.assertEqual(board.size, size)
        self.assertEqual(board.playfield, playfield)
        self.assertEqual(board.rem_pcs_in_rows, rem_pcs_in_rows)
        self.assertEqual(board.rem_pcs_in_cols, rem_pcs_in_cols)
        self.assertEqual(board.playfield is playfield, False)
        self.assertEqual(board.rem_pcs_in_rows is rem_pcs_in_rows, False)
        self.assertEqual(board.rem_pcs_in_cols is rem_pcs_in_cols, False)
        self.assertEqual(board.total_pcs_in_rows, rem_pcs_in_rows)
        self.assertEqual(board.total_pcs_in_cols, rem_pcs_in_cols)
        self.assertEqual(board.total_pcs_in_rows is rem_pcs_in_rows, False)
        self.assertEqual(board.total_pcs_in_cols is rem_pcs_in_cols, False)

        total_pcs_in_rows = [x + random.randrange(5) for x in rem_pcs_in_rows]
        total_pcs_in_cols = [x + random.randrange(5) for x in rem_pcs_in_cols]
        board = bs.Board(
            size, playfield, rem_pcs_in_rows, rem_pcs_in_cols,
            total_pcs_in_rows, total_pcs_in_cols
        )
        self.assertEqual(board.total_pcs_in_rows, total_pcs_in_rows)
        self.assertEqual(board.total_pcs_in_cols, total_pcs_in_cols)
        self.assertEqual(board.total_pcs_in_rows is total_pcs_in_rows, False)
        self.assertEqual(board.total_pcs_in_cols is total_pcs_in_cols, False)

    def test_board_repr(self):
        exp_repr = (
            '═════════════════════════════════════════\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(1)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(3)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(3)\n'
            ' x   x   O   x   x   x   x   x   x   x   ║(1)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(1)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(2)\n'
            ' x   x   .   x   .   x   x   .   x   x   ║(2)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)\n'
            ' x   x   x   x   O   x   x   x   x   x   ║(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(g_exp_board.repr(True), exp_repr)

        exp_repr = (
            '═════════════════════════════════════════\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(0)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(3)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(3)\n'
            ' x   x   O   x   x   x   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(2)\n'
            ' x   x   .   x   .   x   x   .   x   x   ║(0)(2)\n'
            ' x   x   x   x   x   x   x   x   x   x   ║(0)(0)\n'
            ' x   x   x   x   O   x   x   x   x   x   ║(0)(7)\n'
            '═════════════════════════════════════════\n'
            '(0) (0) (0) (0) (0) (0) (0) (0) (0) (0) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(g_exp_board.__repr__(), exp_repr)

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
            12,
            playfield,
            [0, 0, 1, 3, 3, 1, 1, 2, 2, 0, 7, 0],
            [0, 1, 1, 4, 1, 6, 1, 0, 2, 2, 2, 0]
        )
        self.assertEqual(g_exp_board.__eq__(board), True)
        self.assertEqual(g_exp_board is board, False)

        board.playfield[1][1] = bs.FieldType.SEA
        self.assertEqual(g_exp_board.__eq__(board), False)

    def test_board_get_copy(self):
        board = g_exp_board.get_copy()
        self.assertEqual(g_exp_board, board)
        self.assertEqual(g_exp_board is board, False)

    def test_fleet_init(self):
        ship_lengths = random.sample(range(5, 11), 4)
        subfleet_sizes = {l: random.randrange(5) for l in ship_lengths}
        fleet = bs.Fleet(ship_lengths, subfleet_sizes)
        self.assertEqual(
            fleet.ship_lengths, sorted(ship_lengths, reverse=True)
        )
        self.assertEqual(fleet.subfleet_sizes, subfleet_sizes)
        self.assertEqual(fleet.ship_lengths is ship_lengths, False)
        self.assertEqual(fleet.subfleet_sizes is subfleet_sizes, False)

    def test_fleet_repr(self):
        g_exp_fleet_exp_repr = "Fleet(ship_lengths=[4, 3, 2, 1], " \
            "subfleet_sizes={4: 1, 3: 2, 2: 3, 1: 4})"
        self.assertEqual(g_exp_fleet_exp_repr, g_exp_fleet.__repr__())

    def test_fleet_eq(self):
        fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 2, 2: 3, 1: 4})
        self.assertEqual(g_exp_fleet.__eq__(fleet), True)
        self.assertEqual(g_exp_fleet is fleet, False)

        fleet.ship_lengths[0] = 5
        self.assertEqual(g_exp_fleet.__eq__(fleet), False)

    def test_fleet_get_copy(self):
        fleet = g_exp_fleet.get_copy()
        self.assertEqual(g_exp_fleet, fleet)
        self.assertEqual(g_exp_fleet is fleet, False)

    def test_get_redefined_FieldType(self):
        FieldType = bs.get_redefined_FieldType(config)
        self.assertEqual(FieldType.SEA.value, '.')
        self.assertEqual(FieldType.SHIP.value, 'O')
        self.assertEqual(FieldType.UNKNOWN.value, 'x')
        self.assertEqual(FieldType.SEA.__repr__(), '<FieldType.SEA>')

    def test_parse_game_data_file(self):
        exp_playfield = [[bs.FieldType.UNKNOWN] * 10 for _ in range(10)]
        exp_playfield[4][2] = bs.FieldType.SHIP
        exp_playfield[7][2] = bs.FieldType.SEA
        exp_playfield[7][4] = bs.FieldType.SEA
        exp_playfield[7][7] = bs.FieldType.SEA
        exp_playfield[9][4] = bs.FieldType.SHIP
        act_board_size, act_playfield, act_solution_pcs_in_rows, \
            act_solution_pcs_in_cols, act_fleet = \
            bs.parse_game_data_file(config["GAMEDATA"]["FILEPATH"])
        self.assertEqual(act_board_size, 10)
        self.assertEqual(act_playfield, exp_playfield)
        self.assertEqual(
            act_solution_pcs_in_rows, [0, 1, 3, 3, 1, 1, 2, 2, 0, 7]
        )
        self.assertEqual(
            act_solution_pcs_in_cols, [1, 1, 4, 1, 6, 1, 0, 2, 2, 2]
        )
        self.assertEqual(
            act_fleet, bs.Fleet([4, 3, 2, 1], {4: 1, 3: 2, 2: 3, 1: 4})
        )

    def test_get_board_from_input_data(self):
        board_size = 10
        playfield = [[bs.FieldType.UNKNOWN] * 10 for _ in range(10)]
        playfield[4][2] = bs.FieldType.SHIP
        playfield[7][2] = bs.FieldType.SEA
        playfield[7][4] = bs.FieldType.SEA
        playfield[7][7] = bs.FieldType.SEA
        playfield[9][4] = bs.FieldType.SHIP
        rem_pcs_in_rows = [0, 1, 3, 3, 1, 1, 2, 2, 0, 7]
        rem_pcs_in_cols = [1, 1, 4, 1, 6, 1, 0, 2, 2, 2]

        exp_board_size = 12
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
            bs.get_board_from_input_data(
                board_size, playfield, rem_pcs_in_rows, rem_pcs_in_cols
            ),
            bs.Board(
                exp_board_size, exp_playfield, exp_rem_pcs_in_rows,
                exp_rem_pcs_in_cols
            )
        )

    def test_get_ship_pcs_positions(self):
        act_board = g_exp_board.get_copy()
        self.assertEqual(
            bs.get_ship_pcs_positions(act_board), [(5, 3), (10, 5)]
        )
        self.assertEqual(act_board, g_exp_board)

    def test_mark_uncovered_sea_positions(self):
        act_board = g_exp_board.get_copy()
        act_ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        exp_ship_pcs_positions = [*act_ship_pcs_positions]
        bs.mark_uncovered_sea_positions(
            act_board, act_ship_pcs_positions
        )
        exp_board_repr = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' x   x   x   x   x   x   .   x   x   x   ║(0)(1)\n'
            ' x   x   x   x   x   x   .   x   x   x   ║(0)(3)\n'
            ' x   .   x   .   x   x   .   x   x   x   ║(0)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(0)(1)\n'
            ' x   .   x   .   x   x   .   x   x   x   ║(0)(1)\n'
            ' x   x   x   x   x   x   .   x   x   x   ║(0)(2)\n'
            ' x   x   .   x   .   x   .   .   x   x   ║(0)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' x   x   x   x   O   x   .   x   x   x   ║(0)(7)\n'
            '═════════════════════════════════════════\n'
            '(0) (0) (0) (0) (0) (0) (0) (0) (0) (0) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(act_board, self.parse_board(exp_board_repr))
        self.assertEqual(
            act_ship_pcs_positions, exp_ship_pcs_positions
        )

    def test_ship_cannot_exceed_rem_pcs_in_rows(self):
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(3, 7, 4, bs.Direction.RIGHT): False,
            bs.Ship(1, 5, 1, bs.Direction.RIGHT): False,
            bs.Ship(10, 7, 4, bs.Direction.RIGHT): True
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_ship_cannot_exceed_rem_pcs_in_cols(self):
        g_exp_board.rem_pcs_in_rows[9] = 1
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(9, 1, 2, bs.Direction.DOWN): False,
            bs.Ship(9, 7, 2, bs.Direction.DOWN): False,
            bs.Ship(9, 10, 2, bs.Direction.DOWN): True
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_ship_cannot_overflow_row(self):
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(3, 9, 3, bs.Direction.RIGHT): False,
            bs.Ship(3, 8, 3, bs.Direction.RIGHT): True,
            bs.Ship(10, 10, 1, bs.Direction.RIGHT): True
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_ship_cannot_overflow_column(self):
        g_exp_board.playfield[8][8] = bs.FieldType.UNKNOWN
        g_exp_board.rem_pcs_in_rows[9] = 1
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(10, 10, 2, bs.Direction.DOWN): False,
            bs.Ship(9, 10, 2, bs.Direction.DOWN): True
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_all_ship_pcs_in_rows_must_initially_be_unknown(self):
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(10, 2, 4, bs.Direction.RIGHT): False,
            bs.Ship(10, 1, 3, bs.Direction.RIGHT): True,
            bs.Ship(8, 3, 1, bs.Direction.RIGHT): False
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_all_ship_pcs_in_columns_must_initially_be_unknown(self):
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(7, 8, 2, bs.Direction.DOWN): False,
            bs.Ship(6, 8, 2, bs.Direction.DOWN): True
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_ship_must_not_touch_another_ship(self):
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(6, 4, 1, bs.Direction.RIGHT): False,
            bs.Ship(6, 3, 1, bs.Direction.RIGHT): False,
            bs.Ship(6, 2, 1, bs.Direction.RIGHT): False,
            bs.Ship(10, 2, 3, bs.Direction.RIGHT): False,
            bs.Ship(4, 1, 2, bs.Direction.RIGHT): False,
            bs.Ship(4, 1, 3, bs.Direction.RIGHT): False,
            bs.Ship(4, 4, 3, bs.Direction.RIGHT): False,
            bs.Ship(10, 6, 1, bs.Direction.RIGHT): False
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

        g_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        g_exp_board.playfield[4][9] = bs.FieldType.SHIP
        act_board = g_exp_board.get_copy()
        test_data = {
            bs.Ship(5, 10, 2, bs.Direction.DOWN): False,
            bs.Ship(5, 9, 2, bs.Direction.DOWN): False,
            bs.Ship(5, 8, 2, bs.Direction.DOWN): False,
            bs.Ship(4, 8, 2, bs.Direction.DOWN): False,
            bs.Ship(2, 8, 2, bs.Direction.DOWN): False,
            bs.Ship(2, 9, 2, bs.Direction.DOWN): False,
            bs.Ship(2, 10, 2, bs.Direction.DOWN): False,
            bs.Ship(4, 10, 2, bs.Direction.DOWN): False
        }
        for ship, value in test_data.items():
            self.assertEqual(bs.can_fit_ship_on_board(act_board, ship), value)
            self.assertEqual(act_board, g_exp_board)

    def test_reduce_rem_pcs_and_mark_sea_in_filled_rows(self):
        g_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        g_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        g_exp_board.rem_pcs_in_cols[8] = 1
        act_board = g_exp_board.get_copy()
        bs.reduce_board_rem_pcs_and_mark_sea_in_filled_rows_and_cols(
            act_board, bs.Ship(4, 8, 3, bs.Direction.RIGHT)
        )
        g_exp_board.rem_pcs_in_rows[4] = 0
        g_exp_board.rem_pcs_in_cols[8] = 0
        g_exp_board.rem_pcs_in_cols[9] = 1
        g_exp_board.rem_pcs_in_cols[10] = 1
        for i in range(1, 11):
            g_exp_board.playfield[4][i] = bs.FieldType.SEA
            g_exp_board.playfield[i][8] = bs.FieldType.SEA
        self.assertEqual(act_board, g_exp_board)

    def test_reduce_rem_pcs_and_mark_sea_in_filled_columns(self):
        g_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        g_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = g_exp_board.get_copy()
        bs.reduce_board_rem_pcs_and_mark_sea_in_filled_rows_and_cols(
            act_board, bs.Ship(2, 8, 2, bs.Direction.DOWN)
        )
        g_exp_board.rem_pcs_in_cols[8] = 0
        g_exp_board.rem_pcs_in_rows[2] = 0
        g_exp_board.rem_pcs_in_rows[3] = 2
        for i in range(1, 11):
            g_exp_board.playfield[2][i] = bs.FieldType.SEA
            g_exp_board.playfield[i][8] = bs.FieldType.SEA
        self.assertEqual(act_board, g_exp_board)

    def test_mark_ship_in_row(self):
        ship = bs.Ship(10, 2, 4, bs.Direction.RIGHT)
        act_board = g_exp_board.get_copy()
        bs.mark_ship(act_board, ship)
        for i in range(2, 6):
            g_exp_board.playfield[10][i] = bs.FieldType.SHIP
        for i in range(1, 7):
            g_exp_board.playfield[9][i] = bs.FieldType.SEA
            g_exp_board.playfield[11][i] = bs.FieldType.SEA
        g_exp_board.playfield[10][1] = bs.FieldType.SEA
        g_exp_board.playfield[10][6] = bs.FieldType.SEA
        self.assertEqual(act_board, g_exp_board)

    def test_mark_ship_of_size_one(self):
        ship = bs.Ship(2, 1, 1, bs.Direction.RIGHT)
        act_board = g_exp_board.get_copy()
        bs.mark_ship(act_board, ship)
        g_exp_board.playfield[2][1] = bs.FieldType.SHIP
        for i in range(3):
            g_exp_board.playfield[1][i] = bs.FieldType.SEA
            g_exp_board.playfield[3][i] = bs.FieldType.SEA
        g_exp_board.playfield[2][0] = bs.FieldType.SEA
        g_exp_board.playfield[2][2] = bs.FieldType.SEA
        self.assertEqual(act_board, g_exp_board)

    def test_mark_ship_in_column(self):
        ship = bs.Ship(2, 3, 4, bs.Direction.DOWN)
        act_board = g_exp_board.get_copy()
        bs.mark_ship(act_board, ship)
        for i in range(2, 6):
            g_exp_board.playfield[i][3] = bs.FieldType.SHIP
        for i in range(1, 7):
            g_exp_board.playfield[i][2] = bs.FieldType.SEA
        for i in range(1, 7):
            g_exp_board.playfield[i][4] = bs.FieldType.SEA
        g_exp_board.playfield[1][3] = bs.FieldType.SEA
        g_exp_board.playfield[6][3] = bs.FieldType.SEA
        self.assertEqual(act_board, g_exp_board)

    def test_mark_ships_passes(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        for x, y in ship_pcs_positions:
            g_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(g_exp_board, ship_pcs_positions)
        act_board, act_fleet = g_exp_board.get_copy(), g_exp_fleet.get_copy()
        self.assertEqual(
            bs.mark_ships(
                act_board,
                act_fleet,
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(2, 10, 1, bs.Direction.RIGHT),
                    bs.Ship(3, 3, 3, bs.Direction.DOWN)
                ]
            ),
            True
        )
        exp_board_repr = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   .   .   .   .   .   O   ║(1)(1)\n'
            ' x   .   O   .   x   x   .   x   .   .   ║(1)(3)\n'
            ' x   .   O   .   x   x   .   x   x   x   ║(1)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' x   .   .   .   x   x   .   x   x   x   ║(0)(1)\n'
            ' x   .   .   .   x   x   .   x   x   x   ║(0)(2)\n'
            ' x   .   .   .   .   x   .   .   x   x   ║(0)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   O   O   O   O   .   .   x   x   x   ║(4)(7)\n'
            '═════════════════════════════════════════\n'
            '(0) (1) (4) (1) (1) (0) (0) (0) (0) (1) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(act_board, self.parse_board(exp_board_repr))
        self.assertEqual(
            act_fleet, bs.Fleet([4, 3, 2, 1], {4: 0, 3: 1, 2: 3, 1: 3})
        )

    def test_mark_ships_fails_when_ship_pcs_exceeded(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        for x, y in ship_pcs_positions:
            g_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(g_exp_board, ship_pcs_positions)
        self.assertEqual(
            bs.mark_ships(
                g_exp_board,
                g_exp_fleet,
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(2, 10, 1, bs.Direction.RIGHT),
                    bs.Ship(2, 3, 3, bs.Direction.DOWN)
                ]
            ),
            False
        )

    def test_mark_ships_fails_when_ship_pcs_touch(self):
        ship_pcs_positions = [(10, 5)]
        for x, y in ship_pcs_positions:
            g_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(g_exp_board, ship_pcs_positions)
        self.assertEqual(
            bs.mark_ships(
                g_exp_board,
                g_exp_fleet,
                [
                    bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                    bs.Ship(2, 10, 1, bs.Direction.RIGHT),
                    bs.Ship(2, 3, 3, bs.Direction.DOWN)
                ]
            ),
            False
        )

    def test_get_potential_ships_for_ship_piece_position(self):
        bs.mark_uncovered_sea_positions(g_exp_board, [])
        g_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        act_board = g_exp_board.get_copy()
        test_data = {
            (5, 3, 4): [
                bs.Ship(2, 3, 4, bs.Direction.DOWN),
                bs.Ship(3, 3, 4, bs.Direction.DOWN),
                bs.Ship(4, 3, 4, bs.Direction.DOWN)
            ],
            (5, 3, 3): [
                bs.Ship(3, 3, 3, bs.Direction.DOWN),
                bs.Ship(4, 3, 3, bs.Direction.DOWN),
                bs.Ship(5, 3, 3, bs.Direction.DOWN)
            ],
            (5, 3, 2): [
                bs.Ship(4, 3, 2, bs.Direction.DOWN),
                bs.Ship(5, 3, 2, bs.Direction.DOWN)
            ],
            (5, 3, 1): [bs.Ship(5, 3, 1, bs.Direction.RIGHT)]
        }
        for params, value in test_data.items():
            self.assertEqual(
                bs.get_potential_ships_for_ship_piece_position(
                    act_board, *params),
                value
            )
            self.assertEqual(act_board, g_exp_board)

        g_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = g_exp_board.get_copy()
        test_data = {
            (10, 5, 4): [
                bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                bs.Ship(10, 3, 4, bs.Direction.RIGHT)
            ],
            (10, 5, 3): [
                bs.Ship(10, 3, 3, bs.Direction.RIGHT),
                bs.Ship(10, 4, 3, bs.Direction.RIGHT)
            ],
            (10, 5, 2): [
                bs.Ship(10, 4, 2, bs.Direction.RIGHT),
                bs.Ship(10, 5, 2, bs.Direction.RIGHT)
            ],
            (10, 5, 1): [bs.Ship(10, 5, 1, bs.Direction.RIGHT)]
        }
        for params, value in test_data.items():
            self.assertEqual(
                bs.get_potential_ships_for_ship_piece_position(
                    act_board, *params),
                value
            )
            self.assertEqual(act_board, g_exp_board)

    def test_get_potential_ships_for_ship_pcs_positions(self):
        exp_ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        act_ship_positions = [*exp_ship_pcs_positions]
        bs.mark_uncovered_sea_positions(g_exp_board, [])
        g_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        g_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = g_exp_board.get_copy()
        exp_fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 2, 2: 0, 1: 4})
        act_fleet = exp_fleet.get_copy()
        self.assertEqual(
            bs.get_potential_ships_for_ship_pcs_positions(
                act_board, act_fleet, act_ship_positions
            ),
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
                    bs.Ship(10, 5, 1, bs.Direction.RIGHT)
                ]
            }
        )
        self.assertEqual(act_board, g_exp_board)
        self.assertEqual(act_fleet, exp_fleet)
        self.assertEqual(act_ship_positions, exp_ship_pcs_positions)

    def test_reduce_potential_ships_for_ship_pcs_positions_without_delete(
        self
    ):
        exp_ship_pcs_positions = [(5, 3), (5, 5)]
        act_ship_pcs_positions = [*exp_ship_pcs_positions]
        ship = bs.Ship(5, 3, 3, bs.Direction.RIGHT)
        act_potential_ships_for_ship_pcs_positions = {
            (5, 3): [
                bs.Ship(*ship),
                bs.Ship(5, 3, 2, bs.Direction.RIGHT),
                bs.Ship(5, 3, 1, bs.Direction.RIGHT)
            ],
            (5, 5): [
                bs.Ship(*ship),
                bs.Ship(5, 4, 2, bs.Direction.RIGHT),
                bs.Ship(5, 5, 1, bs.Direction.RIGHT)
            ]
        }
        exp_potential_ships_for_ship_pcs_positions = {
            (5, 3): [
                bs.Ship(5, 3, 2, bs.Direction.RIGHT),
                bs.Ship(5, 3, 1, bs.Direction.RIGHT)
            ],
            (5, 5): [
                bs.Ship(5, 4, 2, bs.Direction.RIGHT),
                bs.Ship(5, 5, 1, bs.Direction.RIGHT)
            ]
        }
        bs.reduce_potential_ships_for_ship_pcs_positions(
            act_ship_pcs_positions, act_potential_ships_for_ship_pcs_positions,
            ship
        )
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)
        self.assertEqual(
            act_potential_ships_for_ship_pcs_positions,
            exp_potential_ships_for_ship_pcs_positions
        )

    def test_reduce_potential_ships_for_ship_pcs_positions_with_delete(self):
        exp_ship_pcs_positions = [(5, 3), (5, 6)]
        act_ship_pcs_positions = [*exp_ship_pcs_positions]
        ship = bs.Ship(5, 3, 4, bs.Direction.RIGHT)
        act_potential_ships_for_ship_pcs_positions = {
            (5, 3): [bs.Ship(*ship), bs.Ship(5, 3, 2, bs.Direction.RIGHT)],
            (5, 6): [bs.Ship(*ship)]
        }
        exp_potential_ships_for_ship_pcs_positions = {
            (5, 3): [bs.Ship(5, 3, 2, bs.Direction.RIGHT)]
        }
        bs.reduce_potential_ships_for_ship_pcs_positions(
            act_ship_pcs_positions, act_potential_ships_for_ship_pcs_positions,
            ship
        )
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)
        self.assertEqual(
            act_potential_ships_for_ship_pcs_positions,
            exp_potential_ships_for_ship_pcs_positions
        )

    def test_mark_uncovered_ships(self):
        exp_ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        for x, y in exp_ship_pcs_positions:
            g_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        act_ship_pcs_positions = [*exp_ship_pcs_positions]
        act_potential_ships_for_ship_pcs_positions = {
            (5, 3): [
                bs.Ship(3, 3, 3, bs.Direction.DOWN),
                bs.Ship(4, 3, 3, bs.Direction.DOWN)
            ],
            (10, 5): [bs.Ship(10, 3, 4, bs.Direction.RIGHT)]
        }
        act_board, act_fleet = g_exp_board.get_copy(), g_exp_fleet.get_copy()
        bs.mark_uncovered_ships(
            act_board, act_fleet, act_ship_pcs_positions,
            act_potential_ships_for_ship_pcs_positions
        )
        exp_board_repr = (
            '═════════════════════════════════════════\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(0)\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(3)\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(3)\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   .   x   .   x   x   x   x   ║(0)(2)\n'
            ' x   x   .   .   .   .   x   .   x   x   ║(0)(2)\n'
            ' x   .   .   .   .   .   .   x   x   x   ║(0)(0)\n'
            ' x   .   O   O   O   O   .   x   x   x   ║(4)(7)\n'
            '═════════════════════════════════════════\n'
            '(0) (0) (1) (1) (1) (1) (0) (0) (0) (0) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        g_exp_fleet.subfleet_sizes[4] = 0
        self.assertEqual(act_board, self.parse_board(exp_board_repr))
        self.assertEqual(act_fleet, g_exp_fleet)
        self.assertEqual(act_ship_pcs_positions, exp_ship_pcs_positions)
        self.assertEqual(
            act_potential_ships_for_ship_pcs_positions,
            {
                (5, 3): [
                    bs.Ship(3, 3, 3, bs.Direction.DOWN),
                    bs.Ship(4, 3, 3, bs.Direction.DOWN)
                ]
            }
        )

    def test_get_potential_ships_of_length(self):
        bs.mark_uncovered_sea_positions(
            g_exp_board, bs.get_ship_pcs_positions(g_exp_board)
        )
        g_exp_board.playfield[5][3] = bs.FieldType.UNKNOWN
        g_exp_board.playfield[10][5] = bs.FieldType.UNKNOWN
        act_board = g_exp_board.get_copy()
        test_data = {
            4: [
                bs.Ship(2, 3, 4, bs.Direction.DOWN),
                bs.Ship(3, 3, 4, bs.Direction.DOWN),
                bs.Ship(4, 3, 4, bs.Direction.DOWN),
                bs.Ship(10, 1, 4, bs.Direction.RIGHT),
                bs.Ship(10, 2, 4, bs.Direction.RIGHT),
                bs.Ship(10, 3, 4, bs.Direction.RIGHT)
            ],
            3: [
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
                bs.Ship(10, 8, 3, bs.Direction.RIGHT)
            ]
        }
        for ship_length, potential_ships in test_data.items():
            self.assertEqual(
                bs.get_potential_ships_of_length(act_board, ship_length),
                potential_ships
            )
            self.assertEqual(act_board, g_exp_board)

    def test_find_and_add_solutions_without_some_ship_types(self):
        act_board_repr = (
            '═════════════════════\n'
            ' x   x   x   x   x   ║(0)(0)\n'
            ' x   x   x   x   x   ║(0)(4)\n'
            ' x   x   x   x   x   ║(0)(0)\n'
            ' x   x   x   x   x   ║(0)(1)\n'
            ' x   x   x   x   x   ║(0)(1)\n'
            '═════════════════════\n'
            '(0) (0) (0) (0) (0) \n'
            '(1) (1) (1) (1) (2) \n'
        )
        act_board = self.parse_board(act_board_repr)
        exp_board = act_board.get_copy()
        solution_board_repr = (
            '═════════════════════\n'
            ' .   .   .   .   .   ║(0)(0)\n'
            ' O   O   O   O   .   ║(4)(4)\n'
            ' .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   ║(1)(1)\n'
            ' .   .   .   .   O   ║(1)(1)\n'
            '═════════════════════\n'
            '(1) (1) (1) (1) (2) \n'
            '(1) (1) (1) (1) (2) \n'
        )
        act_fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 0, 2: 1, 1: 0})
        exp_fleet = act_fleet.get_copy()
        act_solutions = []
        bs.find_and_add_solutions(
            act_board, act_fleet, 0, act_solutions
        )
        self.assertEqual(act_board, exp_board)
        self.assertEqual(act_fleet, exp_fleet)
        self.assertEqual(
            act_solutions, [self.parse_board(solution_board_repr)]
        )

    def test_find_and_add_solutions_multiple_ship_positions(self):
        act_board_repr = (
            '═════════════════════════════\n'
            ' .   .   x   x   x   x   x   ║(0)(1)\n'
            ' .   x   x   x   x   x   x   ║(0)(1)\n'
            ' .   x   x   x   x   x   x   ║(0)(2)\n'
            ' .   x   x   x   x   x   x   ║(0)(2)\n'
            ' .   x   x   x   x   x   x   ║(0)(2)\n'
            ' .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   x   x   x   x   x   x   ║(0)(4)\n'
            '═════════════════════════════\n'
            '(0) (0) (0) (0) (0) (0) (0) \n'
            '(0) (5) (1) (1) (1) (1) (3) \n'
        )
        act_board = self.parse_board(act_board_repr)
        exp_board = act_board.get_copy()
        solution_board_repr = (
            '═════════════════════════════\n'
            ' .   .   .   O   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   .   .   O   ║(2)(2)\n'
            ' .   O   .   .   .   .   O   ║(2)(2)\n'
            ' .   O   .   .   .   .   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   O   O   .   O   O   .   ║(4)(4)\n'
            '═════════════════════════════\n'
            '(0) (5) (1) (1) (1) (1) (3) \n'
            '(0) (5) (1) (1) (1) (1) (3) \n'
        )
        act_fleet = bs.Fleet([4, 3, 2, 1], {4: 1, 3: 1, 2: 2, 1: 1})
        exp_fleet = act_fleet.get_copy()
        act_solutions = []
        bs.find_and_add_solutions(
            act_board, act_fleet, 0, act_solutions
        )
        self.assertEqual(act_board, exp_board)
        self.assertEqual(act_fleet, exp_fleet)
        self.assertEqual(
            act_solutions, [self.parse_board(solution_board_repr)]
        )

    def test_get_solution_boards_without_potential_ships(
        self
    ):
        ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        for x, y in ship_pcs_positions:
            g_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(g_exp_board, ship_pcs_positions)
        act_board, act_fleet = g_exp_board.get_copy(), g_exp_fleet.get_copy()
        act_potential_ships_for_ship_pcs_positions = {}
        act_solutions = bs.get_solution_boards(
            act_board, act_fleet, act_potential_ships_for_ship_pcs_positions
        )
        solution1 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' O   .   O   .   O   .   .   .   .   .   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   O   .   O   O   O   .   O   O   O   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution2 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' O   .   O   .   O   .   .   .   .   .   ║(3)(3)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   O   .   O   O   O   .   O   O   O   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution3 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution4 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution5 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   O   .   O   .   .   .   .   .   ║(3)(3)\n'
            ' .   .   .   .   O   .   .   O   O   .   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' O   .   .   .   .   .   .   .   .   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   O   O   O   O   .   O   O   O   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(
            act_solutions,
            [
                self.parse_board(solution1),
                self.parse_board(solution2),
                self.parse_board(solution3),
                self.parse_board(solution4),
                self.parse_board(solution5)
            ]
        )
        self.assertEqual(act_board, g_exp_board)
        self.assertEqual(act_fleet, g_exp_fleet)
        self.assertEqual(act_potential_ships_for_ship_pcs_positions, {})

    def test_get_solution_boards_with_potential_ships(self):
        ship_pcs_positions = bs.get_ship_pcs_positions(g_exp_board)
        for x, y in ship_pcs_positions:
            g_exp_board.playfield[x][y] = bs.FieldType.UNKNOWN
        bs.mark_uncovered_sea_positions(g_exp_board, ship_pcs_positions)
        act_board, act_fleet = g_exp_board.get_copy(), g_exp_fleet.get_copy()
        act_potential_ships_for_ship_pcs_positions = \
            bs.get_potential_ships_for_ship_pcs_positions(
                g_exp_board,
                g_exp_fleet,
                ship_pcs_positions
            )
        exp_potential_ships_for_ship_pcs_positions = {
            **act_potential_ships_for_ship_pcs_positions
        }
        act_solutions = bs.get_solution_boards(
            act_board, act_fleet, act_potential_ships_for_ship_pcs_positions
        )
        solution1 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution2 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution3 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   O   .   O   .   .   .   .   .   ║(3)(3)\n'
            ' .   .   .   .   O   .   .   O   O   .   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' O   .   .   .   .   .   .   .   .   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   O   O   O   O   .   O   O   O   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(
            act_solutions,
            [
                self.parse_board(solution1),
                self.parse_board(solution2),
                self.parse_board(solution3)
            ]
        )
        self.assertEqual(act_board, g_exp_board)
        self.assertEqual(act_fleet, g_exp_fleet)
        self.assertEqual(
            act_potential_ships_for_ship_pcs_positions,
            exp_potential_ships_for_ship_pcs_positions
        )

    def test_parse_test_config(self):
        self.assertEqual(
            "/media/winshare/git/Battleships/tests/sample_boards/board01.txt",
            config["GAMEDATA"]["FILEPATH"]
        )
        self.assertEqual("O", config["FIELDTYPESYMBOLS"]["SHIP"])
        self.assertEqual(".", config["FIELDTYPESYMBOLS"]["SEA"])
        self.assertEqual("x", config["FIELDTYPESYMBOLS"]["UNKNOWN"])

    def test_parse_default_config(self):
        default_config = bs.parse_config()
        self.assertEqual(
            "/media/winshare/git/Battleships/tests/sample_boards/board01.txt",
            default_config["GAMEDATA"]["FILEPATH"]
        )
        self.assertEqual("O", default_config["FIELDTYPESYMBOLS"]["SHIP"])
        self.assertEqual(".", default_config["FIELDTYPESYMBOLS"]["SEA"])
        self.assertEqual("x", default_config["FIELDTYPESYMBOLS"]["UNKNOWN"])

    def test_get_solutions_when_has_solutions(self):
        solution1 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution2 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   O   ║(3)(3)\n'
            ' .   .   O   .   O   .   .   O   .   .   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   .   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   O   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' O   .   O   O   O   O   .   O   O   .   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        solution3 = (
            '═════════════════════════════════════════\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   O   O   .   O   .   .   .   .   .   ║(3)(3)\n'
            ' .   .   .   .   O   .   .   O   O   .   ║(3)(3)\n'
            ' .   .   O   .   .   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   .   .   O   .   .   .   .   .   ║(1)(1)\n'
            ' .   .   O   .   O   .   .   .   .   .   ║(2)(2)\n'
            ' O   .   .   .   .   .   .   .   .   O   ║(2)(2)\n'
            ' .   .   .   .   .   .   .   .   .   .   ║(0)(0)\n'
            ' .   .   O   O   O   O   .   O   O   O   ║(7)(7)\n'
            '═════════════════════════════════════════\n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
            '(1) (1) (4) (1) (6) (1) (0) (2) (2) (2) \n'
        )
        self.assertEqual(
            bs.get_solutions(SAMPLE_CONFIG_FILE_PATH),
            [
                self.parse_board(solution1),
                self.parse_board(solution2),
                self.parse_board(solution3)
            ]
        )

    def test_get_solutions_when_no_solutions(self):
        self.assertEqual(
            bs.get_solutions(SAMPLE_CONFIG_FILE_PATH2), []
        )

    def test_run(self):
        bs.run()
