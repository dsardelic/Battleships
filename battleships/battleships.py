"""Battleship puzzle solver."""

from configparser import ConfigParser
from enum import Enum
import os
from typing import List, Dict, Tuple, Optional, Union, Set, NamedTuple, Any, \
    cast


Position = Tuple[int, int]


class FieldType(Enum):
    """Types of board playfield fields. Currently only the following field
    types are supported: SHIP, SEA, and UNKNOWN.
    """
    SEA = 'SEA'
    SHIP = 'SHIP'
    UNKNOWN = 'UNKNOWN'


PlayField = List[List[FieldType]]


class Direction(Enum):
    """Directions in which a ship can be placed onto the board."""
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'


Ship = NamedTuple(
    "Ship",
    [('row', int), ('col', int), ('length', int), ('direction', Direction)]
)


FieldsShipsMappings = Dict[Position, List[Ship]]


class Fleet(
    NamedTuple(
        "Fleet",
        [("ship_lengths", List[int]), ("subfleet_sizes", Dict[int, int])]
    )
):
    """Class representing a fleet of ships of various lenghts."""
    __slots__ = ()

    def get_copy(self) -> "Fleet":
        """Returns a copy of this object."""
        return self.__class__([*self.ship_lengths], {**self.subfleet_sizes})


GameData = NamedTuple(
    "GameData",
    [
        ("board_size", int),
        ("playfield", PlayField),
        ("solution_pcs_in_rows", List[int]),
        ("solution_pcs_in_cols", List[int]),
        ("fleet", Fleet)
    ]
)


class Board:
    """Class representing board data.

    For practical reasons the playfield actually contains two additional rows
    and two additional columns more than the actual playfield. Therefore, the
    playfield area which may contain ships pieces is within the range
    [1:rows-1][1:columns-1].

    Class instance attributes:
    size - Number of playfield rows and columns. The program currently supports
        square playfields only. Since the playfield contains two additional row
        and two additional columns, the number is greater than the actual
        playfield size by 2.
    playfield - 2D list of variables of type FieldType.
    rem_pcs_in_rows - List of number of ship pieces required to fill each
        playfield row.
    rem_pcs_in_cols - List of number of ship pieces required to fill each
        playfield column.
    total_pcs_in_rows - List of total required number of ship pieces in each
        playfield row.
    total_pcs_in_cols - List of total required number of ship pieces in each
        playfield column.
    """

    def __init__(
        self,
        size: int,
        playfield: PlayField,
        rem_pcs_in_rows: List[int],
        rem_pcs_in_cols: List[int],
        total_pcs_in_rows: Optional[List[int]]=None,
        total_pcs_in_cols: Optional[List[int]]=None
    ) -> None:
        """Initializes a new Board object.

        size - Number of playfield rows and columns.
        playfield - 2D list of variables of type FieldType.
        rem_pcs_in_rows - List of number of ship pieces required to fill each
            playfield row.
        rem_pcs_in_cols - List of number of ship pieces required to fill each
            playfield column.
        total_pcs_in_rows - List of total required number of ship pieces in
            each playfield row.
        total_pcs_in_cols - List of total required number of ship pieces in
            each playfield column.
        """
        self.size = size
        self.playfield = [[*row] for row in playfield]
        self.rem_pcs_in_rows = [*rem_pcs_in_rows]
        self.rem_pcs_in_cols = [*rem_pcs_in_cols]
        if total_pcs_in_rows:
            self.total_pcs_in_rows = [*total_pcs_in_rows]
        else:
            self.total_pcs_in_rows = [*self.rem_pcs_in_rows]
        if total_pcs_in_cols:
            self.total_pcs_in_cols = [*total_pcs_in_cols]
        else:
            self.total_pcs_in_cols = [*self.rem_pcs_in_cols]

    def repr(self, total_pcs_only: bool=False) -> str:
        """A convenient string representation of board data.

        total_pcs_only - Flag indicating whether only total required number of
            ship pieces will be included in the representation or both actual
            and required number of ship pieces.
        """
        rep = ''
        rep += '\u2550'
        for j in range(1, self.size - 1):
            rep += '\u2550\u2550\u2550\u2550'
        rep += '\n'
        for i in range(1, self.size - 1):
            rep += ' '
            for j in range(1, self.size - 1):
                rep += str(self.playfield[i][j].value) + '   '
            rep += '\u2551'
            if total_pcs_only:
                rep += '(' + str(self.total_pcs_in_rows[i]) + ')'
            else:
                rep += (
                    '(' +
                    str(self.total_pcs_in_rows[i] - self.rem_pcs_in_rows[i]) +
                    ')(' +
                    str(self.total_pcs_in_rows[i]) +
                    ')'
                )
            rep += '\n'
        rep += '\u2550'
        for j in range(1, self.size - 1):
            rep += '\u2550\u2550\u2550\u2550'
        rep += '\n'
        if not total_pcs_only:
            for j in range(1, self.size - 1):
                rep += (
                    '(' +
                    str(self.total_pcs_in_cols[j] - self.rem_pcs_in_cols[j]) +
                    ') '
                )
            rep += '\n'
        for j in range(1, self.size - 1):
            rep += '(' + str(self.total_pcs_in_cols[j]) + ') '
        rep += '\n'
        return rep

    def __repr__(self) -> str:
        """Overrides the built-in class method."""
        return self.repr()

    def __eq__(self, other: Any) -> bool:
        """Overrides the built-in class method."""
        if isinstance(other, self.__class__):
            other = cast(Board, other)
            return (
                other.size == self.size and
                other.playfield == self.playfield and
                other.rem_pcs_in_rows == self.rem_pcs_in_rows and
                other.rem_pcs_in_cols == self.rem_pcs_in_cols and
                other.total_pcs_in_rows == self.total_pcs_in_rows and
                other.total_pcs_in_cols == self.total_pcs_in_cols
            )
        return False

    def get_copy(self) -> 'Board':
        """Returns a copy of this object."""
        return self.__class__(
            self.size,
            self.playfield,
            self.rem_pcs_in_rows,
            self.rem_pcs_in_cols,
            self.total_pcs_in_rows,
            self.total_pcs_in_cols
        )


def parse_config(config_file_path=None):
    """Parses the input config file and returns a config object."""
    if not config_file_path:
        config_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Battleships.ini'
        )
    config = ConfigParser()
    config.read(config_file_path)
    return config


def get_redefined_fieldtypes(config) -> Enum:
    """Returns the custom FieldType enum definition based on the
    Battleships.ini file configuration.
    """
    fieldtype_mappings = {}
    for field_name in [field_type.name for field_type in FieldType]:
        fieldtype_mappings[field_name] = config['FIELDTYPESYMBOLS'][field_name]
    return Enum('FieldType', fieldtype_mappings)


def parse_game_data_file(input_file_uri: str) -> GameData:
    """Returns a tuple of data contained in the input file.

    input_file_uri - Input file URI
    """
    with open(input_file_uri, 'r') as file:
        subfleet_count = int(next(file).strip())
        ship_lengths = []  # type: List[int]
        subfleet_sizes = {}  # type: Dict[int, int]
        for _ in range(subfleet_count):
            ship_length, subfleet_size = (
                int(x) for x in next(file).strip().split()
            )
            ship_lengths.append(ship_length)
            subfleet_sizes[ship_length] = subfleet_size
        fleet = Fleet(sorted(ship_lengths, reverse=True), subfleet_sizes)
        board_size = int(next(file).strip())
        solution_pcs_in_rows = [int(x) for x in next(file).strip().split()]
        solution_pcs_in_cols = [int(x) for x in next(file).strip().split()]
        playfield = []  # type: PlayField
        for _ in range(board_size):
            playfield.append([FieldType(ch) for ch in next(file).strip()])
        return GameData(
            board_size,
            playfield,
            solution_pcs_in_rows,
            solution_pcs_in_cols,
            fleet
        )


def get_board(
    board_size: int,
    playfield: PlayField,
    solution_pcs_in_rows: List[int],
    solution_pcs_in_cols: List[int]
) -> Board:
    """Returns a board determined by given inputs.

    board_size - Size of input board.
    playfield - 2D input playfield.
    solution_pcs_in_rows - List of ship pieces in each board row.
    solution_pcs_in_cols - List of ship pieces in each board column.
    """
    new_board_size = board_size + 2
    new_playfield = [[FieldType.SEA] * (board_size + 2)]
    for row in playfield:
        new_playfield.append([FieldType.SEA, *row, FieldType.SEA])
    new_playfield.append([FieldType.SEA] * (board_size + 2))
    new_rem_pcs_in_rows = [0, *solution_pcs_in_rows, 0]
    new_rem_pcs_in_cols = [0, *solution_pcs_in_cols, 0]
    return Board(
        new_board_size, new_playfield, new_rem_pcs_in_rows, new_rem_pcs_in_cols
    )


def get_ship_pcs_positions(board: Board) -> List[Position]:
    """Returns coordinates of board fields containing any ship piece.

    board - The board to check.
    """
    ship_pcs_positions = []  # type: List[Position]
    for row in range(1, board.size - 1):
        for col in range(1, board.size - 1):
            if board.playfield[row][col] == FieldType.SHIP:
                ship_pcs_positions.append((row, col))
    return ship_pcs_positions


def mark_uncovered_sea_positions(
    board: Board,
    ship_pcs_positions: List[Position]
) -> None:
    """Marks sea in those fields where there can be nothing else but sea.

    board - The board to update.
    ship_pcs_positions - Coordinates of board fields containing any ship piece.
    """
    for row, col in ship_pcs_positions:
        board.playfield[row - 1][col - 1] = FieldType.SEA
        board.playfield[row - 1][col + 1] = FieldType.SEA
        board.playfield[row + 1][col - 1] = FieldType.SEA
        board.playfield[row + 1][col + 1] = FieldType.SEA
    for i in range(1, board.size - 1):
        ship_pcs_row = sum(
            board.playfield[i][col] == FieldType.SHIP
            for col in range(1, board.size - 1)
        )
        if ship_pcs_row == board.rem_pcs_in_rows[i]:
            for col in range(1, board.size - 1):
                if board.playfield[i][col] == FieldType.UNKNOWN:
                    board.playfield[i][col] = FieldType.SEA
        ship_pcs_col = sum(
            board.playfield[row][i] == FieldType.SHIP
            for row in range(1, board.size - 1)
        )
        if ship_pcs_col == board.rem_pcs_in_cols[i]:
            for row in range(1, board.size - 1):
                if board.playfield[row][i] == FieldType.UNKNOWN:
                    board.playfield[row][i] = FieldType.SEA


def can_fit_ship_on_board(board: Board, ship: Ship) -> bool:
    """Checks whether ship can be placed on board without violating game rules.

    board - The board onto which to try to place ship.
    ship - The ship to try to place onto board.
    """
    if ship.direction == Direction.RIGHT:
        if ship.length > board.rem_pcs_in_rows[ship.row]:
            return False
        if ship.col + ship.length > board.size - 1:
            return False
        if not all(
            board.playfield[ship.row][col] == FieldType.UNKNOWN
            for col in range(ship.col, ship.col + ship.length)
        ):
            return False
        if any(
            board.playfield[ship.row - 1][col] == FieldType.SHIP
            for col in range(ship.col - 1, ship.col + ship.length + 1)
        ):
            return False
        if any(
            board.playfield[ship.row + 1][col] == FieldType.SHIP
            for col in range(ship.col - 1, ship.col + ship.length + 1)
        ):
            return False
        if board.playfield[ship.row][ship.col - 1] == FieldType.SHIP:
            return False
        if board.playfield[ship.row][ship.col + ship.length] == FieldType.SHIP:
            return False
    else:
        if ship.length > board.rem_pcs_in_cols[ship.col]:
            return False
        if ship.row + ship.length > board.size - 1:
            return False
        if not all(
            board.playfield[row][ship.col] == FieldType.UNKNOWN
            for row in range(ship.row, ship.row + ship.length)
        ):
            return False
        if any(
            board.playfield[row][ship.col - 1] == FieldType.SHIP
            for row in range(ship.row - 1, ship.row + ship.length + 1)
        ):
            return False
        if any(
            board.playfield[row][ship.col + 1] == FieldType.SHIP
            for row in range(ship.row - 1, ship.row + ship.length + 1)
        ):
            return False
        if board.playfield[ship.row - 1][ship.col] == FieldType.SHIP:
            return False
        if board.playfield[ship.row + ship.length][ship.col] == FieldType.SHIP:
            return False
    return True


def reduce_rem_pcs_and_mark_sea(board: Board, ship: Ship) -> None:
    """For each ship piece checks if corresponding row and column are filled
    with enough ship pieces. If yes, marks sea in remaining row/column fields
    with UNKNOWN.

    board - The board to update.
    ship - The ship whose coordinates of pieces to check.
    """
    if ship.direction == Direction.RIGHT:
        board.rem_pcs_in_rows[ship.row] -= ship.length
        if board.rem_pcs_in_rows[ship.row] == 0:
            for col in range(1, board.size - 1):
                if board.playfield[ship.row][col] == FieldType.UNKNOWN:
                    board.playfield[ship.row][col] = FieldType.SEA
        for col in range(ship.col, ship.col + ship.length):
            board.rem_pcs_in_cols[col] -= 1
            if board.rem_pcs_in_cols[col] == 0:
                for row in range(1, board.size - 1):
                    if board.playfield[row][col] == FieldType.UNKNOWN:
                        board.playfield[row][col] = FieldType.SEA
    else:
        board.rem_pcs_in_cols[ship.col] -= ship.length
        if board.rem_pcs_in_cols[ship.col] == 0:
            for row in range(1, board.size - 1):
                if board.playfield[row][ship.col] == FieldType.UNKNOWN:
                    board.playfield[row][ship.col] = FieldType.SEA
        for row in range(ship.row, ship.row + ship.length):
            board.rem_pcs_in_rows[row] -= 1
            if board.rem_pcs_in_rows[row] == 0:
                for col in range(1, board.size - 1):
                    if board.playfield[row][col] == FieldType.UNKNOWN:
                        board.playfield[row][col] = FieldType.SEA


def mark_ship(board: Board, ship: Ship) -> None:
    """Mark ship onto board.

    board - The board onto which to mark ship.
    ship - The ship to mark onto board.
    """
    if ship.direction == Direction.RIGHT:
        for col in range(ship.col - 1, ship.col + ship.length + 1):
            board.playfield[ship.row - 1][col] = FieldType.SEA
            board.playfield[ship.row + 1][col] = FieldType.SEA
        board.playfield[ship.row][ship.col - 1] = FieldType.SEA
        board.playfield[ship.row][ship.col:ship.col + ship.length] = \
            [FieldType.SHIP] * ship.length
        board.playfield[ship.row][ship.col + ship.length] = FieldType.SEA
    else:
        for row in range(ship.row - 1, ship.row + ship.length + 1):
            board.playfield[row][ship.col - 1] = FieldType.SEA
            board.playfield[row][ship.col + 1] = FieldType.SEA
        board.playfield[ship.row - 1][ship.col] = FieldType.SEA
        for row in range(ship.row, ship.row + ship.length):
            board.playfield[row][ship.col] = FieldType.SHIP
        board.playfield[ship.row + ship.length][ship.col] = FieldType.SEA


def mark_ships(
    board: Board,
    fleet: Fleet,
    ships: Union[List[Ship], Set[Ship], Tuple[Ship, ...]]
) -> bool:
    """Tries to mark each ship in 'ships', one after another, onto the board
    then updates remaining fleet accordingly. If successful returns True,
    otherwise False.

    board - The board onto which to mark ships.
    fleet - The fleet of ships remaining to be marked onto board.
    ships - The ships to mark onto board.
    """
    for ship in ships:
        if not can_fit_ship_on_board(board, ship):
            return False
        mark_ship(board, ship)
        fleet.subfleet_sizes[ship.length] -= 1
        reduce_rem_pcs_and_mark_sea(board, ship)
    return True


def get_field_ships(
    board: Board,
    row: int,
    col: int,
    ship_length: int
) -> List[Ship]:
    """Returns a list of ships of length ship_length that can each potentially
    be placed onto the board so that one ship piece occupies the board field
    at coordinates (row, col).

    board - The board onto which to check ship placement.
    row - Board playfield field row index.
    col - Board playfield field column index.
    ship_length - The required ship length.
    """
    ships = []  # type: List[Ship]
    if ship_length <= board.rem_pcs_in_rows[row]:
        min_y = max(col - (ship_length - 1), 0)
        max_y = min(col, board.size - 1 - ship_length)
        for i in range(min_y, max_y + 1):
            ship = Ship(row, i, ship_length, Direction.RIGHT)
            if can_fit_ship_on_board(board, ship):
                ships.append(ship)
    if ship_length <= board.rem_pcs_in_cols[col] and ship_length > 1:
        min_x = max(row - (ship_length - 1), 0)
        max_x = min(row, board.size - 1 - ship_length)
        for i in range(min_x, max_x + 1):
            ship = Ship(i, col, ship_length, Direction.DOWN)
            if can_fit_ship_on_board(board, ship):
                ships.append(ship)
    return ships


def get_fields_ships_mappings(
    board: Board,
    fleet: Fleet,
    ship_pcs_positions: List[Position]
) -> FieldsShipsMappings:
    """Returns a dictionary mapping each field in ship_pcs_positions to a list
    of ships that can each potentially be placed onto the board so that one
    ship piece occupies that particular field.

    board - The board onto which to check ship placement.
    fleet - The fleet of ships yet to be marked onto the board.
    ship_pcs_positions - Coordinates of board fields containing ship pieces.
    """
    ships_for_fields = {}  # type: FieldsShipsMappings
    for row, col in ship_pcs_positions:
        for ship_length in fleet.ship_lengths:
            if fleet.subfleet_sizes[ship_length] > 0:
                ships_for_fields[(row, col)] = (
                    ships_for_fields.get((row, col), []) +
                    get_field_ships(board, row, col, ship_length)
                )
    return ships_for_fields


def remove_ship_from_mappings(
    ship_pcs_positions: List[Position],
    fields_ships_mappings: FieldsShipsMappings,
    ship: Ship
) -> None:
    """Removes from fields_ships_mappings all occurences of
    'ship'. If after removing there are no other potential ships for some
    coordinates, then remove the coordinates and associated empty list from
    ships list for the ship piece coordinates.

    ship_pcs_positions - Coordinates of board fields containing ship pieces.
    fields_ships_mappings - Dictionary mapping each field in
        ship_pcs_positions to a list of ships that can each potentially be
        placed onto the board so that one ship piece occupies that particular
        field.
    ship - The ship to validate fields_ships_mappings against.
    """
    for row, col in ship_pcs_positions:
        if (
            (
                ship.direction == Direction.RIGHT and
                row == ship.row and
                ship.col <= col < ship.col + ship.length
            ) or
            (
                ship.direction == Direction.DOWN and
                col == ship.col and
                ship.row <= row < ship.row + ship.length
            )
        ):
            fields_ships_mappings[(row, col)].remove(ship)
            if len(fields_ships_mappings[(row, col)]) == 0:
                del fields_ships_mappings[(row, col)]


def mark_uncovered_ships(
    board: Board,
    fleet: Fleet,
    ship_pcs_positions: List[Position],
    fields_ships_mappings: FieldsShipsMappings
) -> None:
    """Marks ships onto board on those coordinates on which only one ship from
    fields_ships_mappings can be placed and updates fleet
    accordingly.

    board - The board onto which to mark ships.
    fleet - The fleet of ships yet to be marked onto the board.
    ship_pcs_positions - Coordinates of board fields containing ship pieces.
    fields_ships_mappings - Dictionary of potential ships
        which can be placed on a particular field containing any ship piece.
    """
    for row, col in ship_pcs_positions:
        if len(fields_ships_mappings[(row, col)]) == 1:
            ship = fields_ships_mappings[(row, col)][0]
            mark_ships(board, fleet, [ship])
            remove_ship_from_mappings(
                ship_pcs_positions,
                fields_ships_mappings,
                ship
            )


def get_ships_of_length(board: Board, ship_length: int) -> List[Ship]:
    """Returns a list of all possible ships of length ship_length which can be
    placed onto any board field.

    board - The board against which to check ship placement.
    ship_length - Length of ship.
    """
    ships = []  # type: List[Ship]
    for row in range(1, board.size - 1):
        for col in range(1, board.size - 1):
            if board.playfield[row][col] == FieldType.UNKNOWN:
                if (
                    ship_length <= board.rem_pcs_in_rows[row] and
                    col + ship_length < board.size
                ):
                    ship = Ship(row, col, ship_length, Direction.RIGHT)
                    if can_fit_ship_on_board(board, ship):
                        ships.append(ship)
                if (
                    ship_length <= board.rem_pcs_in_cols[col] and
                    row + ship_length < board.size and
                    ship_length > 1
                ):
                    ship = Ship(row, col, ship_length, Direction.DOWN)
                    if can_fit_ship_on_board(board, ship):
                        ships.append(ship)
    return ships


def find_solutions_for_subfleet(
    board: Board,
    fleet: Fleet,
    subfleet_index: int,
    solutions: List[Board]
) -> None:
    """Searches for solutions for given board and given fleet starting at
    subfleet index 'subfleet_index'. If found, adds solution to 'solutions'.

    board - Board for which to find solutions.
    fleet - Fleet for which to find solutions.
    subfleet_index - Index of current fleet ship type to check.
    solutions - List of game solutions.
    """
    subfleet_size = fleet.subfleet_sizes[fleet.ship_lengths[subfleet_index]]
    if subfleet_size == 0:
        if subfleet_index + 1 < len(fleet.ship_lengths):
            find_solutions_for_subfleet(
                board, fleet, subfleet_index + 1, solutions
            )
        else:
            solutions.append(board)
    else:
        ships = get_ships_of_length(
            board, fleet.ship_lengths[subfleet_index]
        )
        if len(ships) == subfleet_size:
            new_board, new_fleet = board.get_copy(), fleet.get_copy()
            if mark_ships(new_board, new_fleet, ships):
                if subfleet_index + 1 < len(fleet.ship_lengths):
                    find_solutions_for_subfleet(
                        new_board, new_fleet, subfleet_index + 1, solutions
                    )
                else:
                    solutions.append(new_board)
        else:
            import itertools
            for ship_combination in itertools.combinations(
                ships, subfleet_size
            ):
                new_board, new_fleet = board.get_copy(), fleet.get_copy()
                if mark_ships(new_board, new_fleet, ship_combination):
                    if subfleet_index + 1 < len(fleet.ship_lengths):
                        find_solutions_for_subfleet(
                            new_board, new_fleet, subfleet_index + 1, solutions
                        )
                    else:
                        solutions.append(new_board)


def get_solutions_for_mappings(
    board: Board,
    fleet: Fleet,
    fields_ships_mappings: FieldsShipsMappings
) -> List[Board]:
    """Returns a list of solutions for given board, given fleet and given list
    of potential ships that occupy board positions where ship pieces are
    located.

    board - Board for which to find solutions.
    fleet - Fleet of ships to be marked onto the board.
    fields_ships_mappings - Dictionary of potential ships that
        can be placed on a particular board field containing any ship piece.
    """
    def ship_combination_exceeds_fleet(
        fleet: Fleet,
        ship_combination: Union[List[Ship], Set[Ship]]
    ) -> bool:
        """For each ship type in ship_combination checks if there are more
        ships in the ship_combination than in the fleet.

        fleet - Fleet against which to check number of ships.
        ship_combination - Group of ships.
        """
        combination_fleet_sizes = {}  # type: Dict[int, int]
        for ship in ship_combination:
            combination_fleet_sizes[ship.length] = \
                combination_fleet_sizes.get(ship.length, 0) + 1
            if (
                combination_fleet_sizes[ship.length] >
                fleet.subfleet_sizes[ship.length]
            ):
                return True
        return False

    solutions = []  # type: List[Board]
    if len(fields_ships_mappings) == 0:
        find_solutions_for_subfleet(board, fleet, 0, solutions)
    else:
        from itertools import product
        for ship_combination in product(
            *fields_ships_mappings.values()
        ):
            ship_combination = set(ship_combination)
            if not ship_combination_exceeds_fleet(fleet, ship_combination):
                new_board, new_fleet = board.get_copy(), fleet.get_copy()
                if mark_ships(new_board, new_fleet, ship_combination):
                    find_solutions_for_subfleet(
                        new_board, new_fleet, 0, solutions
                    )
    return solutions


def get_solutions(config_file_path: str=None) -> List[Board]:
    """Returns a list of solutions for input parameters given in the file at
    location 'game_data_file_path'.

    game_data_file_path - URI of file containing board and fleet data.
    """
    config = parse_config(config_file_path)
    global FieldType
    FieldType = get_redefined_fieldtypes(config)  # type: ignore
    game_data = parse_game_data_file(config["GAMEDATA"]["FILEPATH"])
    board = get_board(
        game_data.board_size,
        game_data.playfield,
        game_data.solution_pcs_in_rows,
        game_data.solution_pcs_in_cols
    )
    ship_pcs_positions = get_ship_pcs_positions(board)
    mark_uncovered_sea_positions(board, ship_pcs_positions)
    for row, col in ship_pcs_positions:
        board.playfield[row][col] = FieldType.UNKNOWN
    fields_ships_mappings = get_fields_ships_mappings(
        board, game_data.fleet, ship_pcs_positions
    )
    mark_uncovered_ships(
        board, game_data.fleet, ship_pcs_positions, fields_ships_mappings
    )
    return get_solutions_for_mappings(
        board, game_data.fleet, fields_ships_mappings
    )


def run() -> None:
    """Searches for and prints the solutions."""
    solutions = get_solutions()
    for solution in solutions:
        print(solution.repr(True))
    if solutions:
        print("{} solutions in total.".format(len(solutions)))
    else:
        print('No solutions found.')


if __name__ == "__main__":
    run()
