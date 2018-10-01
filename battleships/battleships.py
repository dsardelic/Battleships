"""Battleships puzzle solver.

Before running this module please read the README file.
"""

from configparser import ConfigParser
from enum import Enum
import os
from typing import List, Dict, Tuple, Optional, Union, Set, NamedTuple, Any, \
    cast


Position = Tuple[int, int]
"""Specific field coordinates"""


class FieldType(Enum):
    """Types of board fields. Currently only the following field types are
    supported: SHIP, SEA, and UNKNOWN.
    """
    SEA = 'SEA'
    SHIP = 'SHIP'
    UNKNOWN = 'UNKNOWN'


PlayField = List[List[FieldType]]
"""Board playfield - 2D matrix of fields of type FieldType"""


class Direction(Enum):
    """Directions in which a ship can be placed onto the board."""
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'


Ship = NamedTuple(
    "Ship",
    [('row', int), ('col', int), ('length', int), ('direction', Direction)]
)
"""Battleship uniquely defined by its coordinates, length and direction."""


FieldsShipsMappings = Dict[Position, List[Ship]]
"""Dictionary of fields (keys) and corresponding list of ships that occupy that
field (values)."""


class Fleet(
    NamedTuple(
        "Fleet",
        [("ship_lengths", List[int]), ("subfleet_sizes", Dict[int, int])]
    )
):
    """Class representing a fleet of ships of different lenghts. Each length in
    ship_length (key) is mapped to a number of ships of that length (value).
    """
    __slots__ = ()

    def get_copy(self) -> "Fleet":
        """Returns a deep copy of this object.

        Returns:
            Fleet: A copy of this object.
        """
        return self.__class__([*self.ship_lengths], {**self.subfleet_sizes})


GameData = NamedTuple(
    "GameData",
    [
        ("playfield", PlayField),
        ("solution_pcs_in_rows", List[int]),
        ("solution_pcs_in_cols", List[int]),
        ("fleet", Fleet)
    ]
)
"""Data structure containing data parsed from the input data file."""


class Board:
    """Class representing board data.

    A board consists of a playfield whose every row and column is assigned two
    numbers:
        1) number of undetected ship pieces in a particular row or column,
        2) total number of ship pieces in a particular row or column.

    For practical reasons the playfield contains one additional row and one
    additional column at the beginning and the end of the playfield. Therefore,
    the playfield area which may contain ship pieces is within the range
    [1 : rows-1][1 : columns-1].

    Class instance attributes:
        playfield (Playfield): 2D list of variables of type FieldType.
        rem_pcs_in_rows (List[int]): List of number of ship pieces remaining
            to fill each playfield row.
        rem_pcs_in_cols (List[int]): List of number of ship pieces remaining to
            fill each playfield column.
        total_pcs_in_rows (List[int]): List of total required number of ship
            pieces in each playfield row.
        total_pcs_in_cols (List[int]): List of total required number of ship
            pieces in each playfield column.
    """

    def __init__(
        self,
        playfield: PlayField,
        rem_pcs_in_rows: List[int],
        rem_pcs_in_cols: List[int],
        total_pcs_in_rows: Optional[List[int]]=None,
        total_pcs_in_cols: Optional[List[int]]=None
    ) -> None:
        """Initializes a new Board object.

        Args:
            playfield (Playfield): 2D list of variables of type FieldType.
            rem_pcs_in_rows (List[int]): List of number of ship pieces
                remaining to fill each playfield row.
            rem_pcs_in_cols (List[int]): List of number of ship pieces
                remaining to fill each playfield column.
            total_pcs_in_rows (List[int]): List of total required number of
                ship pieces in each playfield row. Defaults to None, in which
                case a copy of the rem_pcs_in_rows list is used.
            total_pcs_in_cols (List[int]): List of total required number of
                ship pieces in each playfield column. Defaults to None, in
                which case a copy of the rem_pcs_in_columns list is used.
        """
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

    @property
    def size(self):
        """Total number of this board playfield rows and columns."""
        return len(self.playfield)

    def repr(self, total_pcs_only: bool=False) -> str:
        """A convenient string representation of this object data.

        Args:
            total_pcs_only (bool): Flag indicating whether only total required
                number of ship pieces will be included in the representation or
                both actual and required number of ship pieces. Defaults to
                False, in which case both numbers are included.

        Returns:
            str: String representation of board data.
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
                other.playfield == self.playfield and
                other.rem_pcs_in_rows == self.rem_pcs_in_rows and
                other.rem_pcs_in_cols == self.rem_pcs_in_cols and
                other.total_pcs_in_rows == self.total_pcs_in_rows and
                other.total_pcs_in_cols == self.total_pcs_in_cols
            )
        return False

    def get_copy(self) -> 'Board':
        """Returns a deep copy of this object.

        Returns:
            Board: A copy of this object.
        """
        return self.__class__(
            self.playfield,
            self.rem_pcs_in_rows,
            self.rem_pcs_in_cols,
            self.total_pcs_in_rows,
            self.total_pcs_in_cols
        )


def parse_config(config_file_path: str=None) -> ConfigParser:
    """Parses the input config file and returns a config object.

    Args:
        config_file_path (str): Configuration file path. Defaults to None, in
            which case the package default INI file is used.

    Returns:
        ConfigParser: Configuration object parsed from the input file.
    """
    if not config_file_path:
        config_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Battleships.ini'
        )
    config = ConfigParser()
    config.read(config_file_path)
    return config


def get_redefined_fieldtypes(config: ConfigParser) -> Enum:
    """Returns a modified FieldType enum definition, based on the game
    configuration.

    Args:
        config (ConfigParser): Game configuration object.

    Returns:
        Enum: Redefined FieldType enum.
    """
    fieldtype_mappings = {}
    for field_name in [field_type.name for field_type in FieldType]:
        fieldtype_mappings[field_name] = config['FIELDTYPESYMBOLS'][field_name]
    return Enum('FieldType', fieldtype_mappings)


def parse_game_data_file(input_file_path: str) -> GameData:
    """Returns data contained in the game input file.

    Args:
        input_file_path (str): Game input file path.

    Returns:
        GameData: Parsed game data.
    """
    with open(input_file_path, 'r') as file:
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
            playfield,
            solution_pcs_in_rows,
            solution_pcs_in_cols,
            fleet
        )


def get_board(
    playfield: PlayField,
    solution_pcs_in_rows: List[int],
    solution_pcs_in_cols: List[int]
) -> Board:
    """Returns a new board object initialized with given inputs. The new board
    contains only sea fields.

    Args:
        playfield (PlayField): Board playfield area which may contain ship
            pieces.
        solution_pcs_in_rows (List[int]): List of ship pieces in each playfield
            row.
        solution_pcs_in_cols (List[int]): List of ship pieces in each playfield
            column.

    Returns:
        Board: Board containing only sea fields.
    """
    new_playfield = [[FieldType.SEA] * (len(playfield) + 2)]
    for row in playfield:
        new_playfield.append([FieldType.SEA, *row, FieldType.SEA])
    new_playfield.append([FieldType.SEA] * (len(playfield) + 2))
    new_rem_pcs_in_rows = [0, *solution_pcs_in_rows, 0]
    new_rem_pcs_in_cols = [0, *solution_pcs_in_cols, 0]
    return Board(
        new_playfield,
        new_rem_pcs_in_rows,
        new_rem_pcs_in_cols
    )


def get_ship_pcs_positions(board: Board) -> List[Position]:
    """Determines which board fields contain a ship piece.

    Args:
        board (Board): The board to check.

    Returns:
        List[Position]: List of board fields containing any ship piece.
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
    """Marks sea in those board fields where there can be nothing else but sea.
    Modifies board content in-place.

    Args:
        board (Board): The board to check and possibly update.
        ship_pcs_positions (List[Position]): Coordinates of board fields
            containing any ship piece.
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
    """Checks whether a sinle ship can be placed onto the board without
    violating game rules.

    Args:
        board (Board): The board onto which to try to place the ship.
        ship (Ship): The ship to try to place onto the board.

    Returns:
        bool: True if successful, False otherwise.
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
    with the maximum allowed number of ship pieces. If yes, marks sea in
    remaining row/column fields with UNKNOWN.

    Args:
        board (Board): The board to check and possibly update.
        ship (Ship): The ship whose placement (rows and columns) to check.
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
    """Mark a ship onto the board. The board is modified in-place.

    Args:
        board (Board): The board onto which to mark the ship.
        ship (Ship): The ship to mark onto the board.
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
    """Checks whether each ship in ships, one after another, can be placed
    onto the board. Modifies the board and fleet in-place. After placing each
    ship, the remaining fleet is updated accordingly.

    Args:
        board (Board): The board onto which to mark the ships.
        fleet (Fleet): The fleet of ships remaining to be marked onto board.
        ships (Union[List[Ship], Set[Ship], Tuple[Ship, ...]]): The ships to
            mark onto the board.

    Returns:
        True if all ships can be marked, False otherwise.
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
    """Determines ships of length ship_length that can each, one at a time,
    possibly be placed onto the board so that each ship occupies the field at
    coordinates (row, col).

    Args:
        board (Board): The board onto which to check ship placement.
        row (int): Board field row index.
        col (int): Board field column index.
        ship_length (int): The required ship length.

    Returns:
        List[Ship]: List of ships of length ship_length that can possibly be
            placed onto the board so that each ship occupies the board field at
            coordinates (row, col).
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
    """For each field in ship_pcs_positions determines a list of ships that can
    each potentially be placed onto the board so that a piece of that ship
    occupies that same field.

    Args:
        board (Board): The board onto which to check ship placement.
        fleet (Fleet): The fleet of ships to be marked onto the board.
        ship_pcs_positions (List[Position]): Coordinates of board fields
            containing ship pieces.

    Returns:
        FieldsShipsMappings: Dictionary of ship fields (keys) and corresponding
            list of ships that can possibly occupy that field (values).
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
    """Removes from fields_ships_mappings all occurences of ship. If after
    removing the ship there are no other possible ships for some coordinates,
    remove the coordinates and associated empty list from the ships list
    corresponding to those coordinates. Modifies fields_ships_mappings
    in-place.

    Args:
        ship_pcs_positions (List[Position]): Coordinates of board fields
            containing ship pieces.
        fields_ships_mappings (FieldsShipsMappings): Dictionary of ship fields
            (keys) and corresponding list of ships that can possibly occupy
            that field (values).
        ship (Ship): The ship to validate fields_ships_mappings against.
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
    """Where a particular field can be occupied with only one ship, marks that
    ship onto the board and removes the ship from the fleet. Modifies the board
    and fleet objects in-place.

    Args:
        board (Board): Board onto which to mark ships.
        fleet (Fleet): Fleet of ships to be marked onto the board.
        ship_pcs_positions (List[Position]): Coordinates of board fields
            containing ship pieces.
        fields_ships_mappings (FieldsShipsMappings): Dictionary of ship fields
            (keys) and corresponding list of ships that can possibly occupy
            that field (values).
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
    """Searches for ships of length ship_length that can be placed anywhere on
    the board.

    Args:
        board (Board): The board against which to check ship placement.
        ship_length (int): Length of ship.

    Returns:
        List[Ship]: List of ships of length ship_length that can be placed onto
        the board.
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
    """Searches for solutions for given board and given fleet and given
    subfleet index. If last remaining subfleet has been marked, adds the board
    to the list of solutions.

    Args:
        board (Board): Board for which to find solutions.
        fleet (Fleet): Fleet of ships to place onto the board.
        subfleet_index (int): Index of subfleet to check.
        solutions (List[Board]): List of found solution boards.
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
    """For each field in fields_ships_mappings a ship from the corresponding
    ship list is selected in order to mark onto the board and occupy that
    field. When all fields are successfully covered, removes the used ships
    from the fleet and searches for solutions for the partially covered board
    and the remaining fleet. Modifies the board and fleet object in-place.

    Args:
        board (Board): Board for which to find solutions.
        fleet (Fleet): Fleet of ships to be marked onto the board.
        fields_ships_mappings (FieldsShipsMappings): Dictionary of ship fields
            (keys) and corresponding list of ships that can possibly occupy
            that field (values).

    Returns:
        List[Board]: List of found solutions boards.
    """

    def ship_combination_exceeds_fleet(
        fleet: Fleet,
        ship_combination: Union[List[Ship], Set[Ship]]
    ) -> bool:
        """For each ship type in ship_combination checks if there are more
        ships in the ship_combination than in the fleet.

        Args:
            fleet (Fleet): Fleet against which to check number of ships.
            ship_combination (Union[List[Ship], Set[Ship]]): Group of ships.

        Returns:
            True if exceeds, False otherwise.
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
        for ship_combination in product(*fields_ships_mappings.values()):
            ship_combination = set(ship_combination)
            if not ship_combination_exceeds_fleet(fleet, ship_combination):
                new_board, new_fleet = board.get_copy(), fleet.get_copy()
                if mark_ships(new_board, new_fleet, ship_combination):
                    find_solutions_for_subfleet(
                        new_board, new_fleet, 0, solutions
                    )
    return solutions


def get_solutions(config_file_path: str=None) -> List[Board]:
    """Returns a list of solutions for input parameters from the file at path
    game_data_file_path.

    Args:
        config_file_path (str): Path of the file containing board and fleet
            data. Defaults to None, in which case the package default
            configuration file is used.

    Returns:
        List[Board]: List of found solution boards.
    """
    config = parse_config(config_file_path)
    global FieldType
    FieldType = get_redefined_fieldtypes(config)  # type: ignore
    game_data = parse_game_data_file(config["GAMEDATA"]["FILEPATH"])
    board = get_board(
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
    """Searches for and prints the game solutions."""
    solutions = get_solutions()
    for solution in solutions:
        print(solution.repr(True))
    if solutions:
        print("{} solutions in total.".format(len(solutions)))
    else:
        print('No solutions found.')


if __name__ == "__main__":
    run()
