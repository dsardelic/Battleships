from enum import Enum
import sys
from typing import List, Dict, Tuple, Optional, Union, Set, NamedTuple, Any


class FieldType(Enum):
    """Types of board playfield fields. Currently only the following field
    types are supported: SHIP, SEA, and UNKNOWN.
    """
    SEA = 'SEA'
    SHIP = 'SHIP'
    UNKNOWN = 'UNKNOWN'


class Direction(Enum):
    """Directions in which a ship can be placed onto the board."""
    RIGHT = 'RIGHT'
    DOWN = 'DOWN'

    def __repr__(self):
        return '<Direction.{}>'.format(self.name)


Ship = NamedTuple(
    'Ship',
    [('x', int), ('y', int), ('length', int), ('direction', Direction)]
)


class Board():
    """Class containing board data.

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
        playfield: List[List[FieldType]],
        rem_pcs_in_rows: List[int],
        rem_pcs_in_cols: List[int],
        total_pcs_in_rows: Optional[List[int]] = None,
        total_pcs_in_cols: Optional[List[int]] = None
    ) -> None:
        """Board class constructor.

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

    def repr(self, total_pcs_only: bool = False) -> str:
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
                    '(' + str(
                        self.total_pcs_in_rows[i] - self.rem_pcs_in_rows[i]
                    ) + ')(' + str(self.total_pcs_in_rows[i]) + ')'
                )
            rep += '\n'
        rep += '\u2550'
        for j in range(1, self.size - 1):
            rep += '\u2550\u2550\u2550\u2550'
        rep += '\n'
        if not total_pcs_only:
            for j in range(1, self.size - 1):
                rep += (
                    '(' + str(
                        self.total_pcs_in_cols[j] - self.rem_pcs_in_cols[j]
                    ) + ') '
                )
            rep += '\n'
        for j in range(1, self.size - 1):
            rep += '(' + str(self.total_pcs_in_cols[j]) + ') '
        rep += '\n'
        return rep

    def __repr__(self) -> str:
        """Overrides the built-in class method."""
        return self.repr()

    def __eq__(self, board: Any) -> bool:
        """Overrides the built-in class method."""
        return (
            type(board) == self.__class__ and
            board.size == self.size and
            board.playfield == self.playfield and
            board.rem_pcs_in_rows == self.rem_pcs_in_rows and
            board.rem_pcs_in_cols == self.rem_pcs_in_cols and
            board.total_pcs_in_rows == self.total_pcs_in_rows and
            board.total_pcs_in_cols == self.total_pcs_in_cols
        )

    def get_copy(self) -> 'Board':
        """Returns a copy of this object."""
        return self.__class__(
            self.size, self.playfield, self.rem_pcs_in_rows,
            self.rem_pcs_in_cols, self.total_pcs_in_rows,
            self.total_pcs_in_cols
        )


class Fleet():
    """Class containing ship fleet data.

    Class instance attributes:
    ship_lengths - List of distinct lengths of fleet ships. Should be sorted in
        descending order so that locations of ships with maximum information
        content are determined first.
    subfleet_sizes - Dictionary of total number of fleet ships of particular
        length (i.e. size of subfleet) for each ship length (i.e. subfleet ship
        type).
    """

    def __init__(
        self,
        ship_lengths: List[int],
        subfleet_sizes: Dict[int, int]
    ) -> None:
        """Fleet class constructor.

        ship_lengths - List of distinct lengths of fleet ships.
        subfleet_sizes - Dictionary of total number of fleet ships of
            particular length (i.e. size of subfleet) for each ship length
            (i.e. subfleet ship type).
        """
        self.ship_lengths = sorted([*ship_lengths], reverse=True)
        self.subfleet_sizes = {**subfleet_sizes}

    def __repr__(self):
        """Overrides the built-in class method."""
        return 'Fleet(ship_lengths={}, subfleet_sizes={})'.format(
            self.ship_lengths, self.subfleet_sizes
        )

    def __eq__(self, fleet: Any) -> bool:
        """Overrides the built-in class method."""
        return (
            type(fleet) == self.__class__ and
            fleet.ship_lengths == self.ship_lengths and
            fleet.subfleet_sizes == self.subfleet_sizes
        )

    def get_copy(self) -> 'Fleet':
        """Returns a copy of this object."""
        return self.__class__(self.ship_lengths, self.subfleet_sizes)


def get_redefined_FieldType_from_ini_file(ini_file_uri: str):
    """Returns a custom definition of the FieldType enum.

    Field types and their corresponding symbols are defined within the
    [FieldTypeSymbols] section of the Battleships.ini configuration file.
    """
    fieldtype_mappings = {}  # type: Dict[str, str]
    with open(ini_file_uri) as prop_file:
        import configparser
        cp = configparser.ConfigParser()
        cp.read_file(prop_file, ini_file_uri)
        for field_name in [field_type.name for field_type in FieldType]:
            fieldtype_mappings[field_name] = cp.get(
                'FieldTypeSymbols', field_name
            )
        redefined_FieldType = Enum('FieldType', fieldtype_mappings)
        redefined_FieldType.__repr__ = \
            lambda self: '<FieldType.{}>'.format(self.name)
        return redefined_FieldType


def get_data_from_file(input_file_uri: str) -> Tuple[
    int, List[List[FieldType]], List[int], List[int], Fleet
]:
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
        fleet = Fleet(ship_lengths, subfleet_sizes)
        board_size = int(next(file).strip())
        solution_pcs_in_rows = [int(x) for x in next(file).strip().split()]
        solution_pcs_in_cols = [int(x) for x in next(file).strip().split()]
        playfield = []  # type: List[List[FieldType]]
        for _ in range(board_size):
            playfield.append([FieldType(ch) for ch in next(file).strip()])
    return board_size, playfield, solution_pcs_in_rows, solution_pcs_in_cols, \
        fleet


def get_board_from_input_data(
    board_size: int,
    playfield: List[List[FieldType]],
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


def get_ship_pcs_positions(board: Board) -> List[Tuple[int, int]]:
    """Returns coordinates of board fields containing any ship piece.

    board - The board to check.
    """
    ship_pcs_positions = []  # type: List[Tuple[int, int]]
    for row in range(1, board.size - 1):
        for col in range(1, board.size - 1):
            if board.playfield[row][col] == FieldType.SHIP:
                ship_pcs_positions.append((row, col))
    return ship_pcs_positions


def mark_uncovered_sea_positions(
    board: Board,
    ship_pcs_positions: List[Tuple[int, int]]
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
        if ship.length > board.rem_pcs_in_rows[ship.x]:
            return False
        if ship.y + ship.length > board.size - 1:
            return False
        if not all(
            board.playfield[ship.x][col] == FieldType.UNKNOWN
            for col in range(ship.y, ship.y + ship.length)
        ):
            return False
        if any(
            board.playfield[ship.x - 1][col] == FieldType.SHIP
            for col in range(ship.y - 1, ship.y + ship.length + 1)
        ):
            return False
        if any(
            board.playfield[ship.x + 1][col] == FieldType.SHIP
            for col in range(ship.y - 1, ship.y + ship.length + 1)
        ):
            return False
        if board.playfield[ship.x][ship.y - 1] == FieldType.SHIP:
            return False
        if board.playfield[ship.x][ship.y + ship.length] == FieldType.SHIP:
            return False
    else:
        if ship.length > board.rem_pcs_in_cols[ship.y]:
            return False
        if ship.x + ship.length > board.size - 1:
            return False
        if not all(
            board.playfield[row][ship.y] == FieldType.UNKNOWN
            for row in range(ship.x, ship.x + ship.length)
        ):
            return False
        if any(
            board.playfield[row][ship.y - 1] == FieldType.SHIP
            for row in range(ship.x - 1, ship.x + ship.length + 1)
        ):
            return False
        if any(
            board.playfield[row][ship.y + 1] == FieldType.SHIP
            for row in range(ship.x - 1, ship.x + ship.length + 1)
        ):
            return False
        if board.playfield[ship.x - 1][ship.y] == FieldType.SHIP:
            return False
        if board.playfield[ship.x + ship.length][ship.y] == FieldType.SHIP:
            return False
    return True


def reduce_board_rem_pcs_and_mark_sea_in_filled_rows_and_cols(
    board: Board, ship: Ship
) -> None:
    """For each ship piece checks if corresponding row and column are filled
    with enough ship pieces. If yes, marks sea in remaining row/column fields
    with UNKNOWN.

    board - The board to update.
    ship - The ship whose coordinates of pieces to check.
    """
    if ship.direction == Direction.RIGHT:
        board.rem_pcs_in_rows[ship.x] -= ship.length
        if board.rem_pcs_in_rows[ship.x] == 0:
            for col in range(1, board.size - 1):
                if board.playfield[ship.x][col] == FieldType.UNKNOWN:
                    board.playfield[ship.x][col] = FieldType.SEA
        for col in range(ship.y, ship.y + ship.length):
            board.rem_pcs_in_cols[col] -= 1
            if board.rem_pcs_in_cols[col] == 0:
                for row in range(1, board.size - 1):
                    if board.playfield[row][col] == FieldType.UNKNOWN:
                        board.playfield[row][col] = FieldType.SEA
    else:
        board.rem_pcs_in_cols[ship.y] -= ship.length
        if board.rem_pcs_in_cols[ship.y] == 0:
            for row in range(1, board.size - 1):
                if board.playfield[row][ship.y] == FieldType.UNKNOWN:
                    board.playfield[row][ship.y] = FieldType.SEA
        for row in range(ship.x, ship.x + ship.length):
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
        for col in range(ship.y - 1, ship.y + ship.length + 1):
            board.playfield[ship.x - 1][col] = FieldType.SEA
            board.playfield[ship.x + 1][col] = FieldType.SEA
        board.playfield[ship.x][ship.y - 1] = FieldType.SEA
        board.playfield[ship.x][ship.y:ship.y + ship.length] = (
            [FieldType.SHIP] * ship.length
        )
        board.playfield[ship.x][ship.y + ship.length] = FieldType.SEA
    else:
        for row in range(ship.x - 1, ship.x + ship.length + 1):
            board.playfield[row][ship.y - 1] = FieldType.SEA
            board.playfield[row][ship.y + 1] = FieldType.SEA
        board.playfield[ship.x - 1][ship.y] = FieldType.SEA
        for row in range(ship.x, ship.x + ship.length):
            board.playfield[row][ship.y] = FieldType.SHIP
        board.playfield[ship.x + ship.length][ship.y] = FieldType.SEA


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
        reduce_board_rem_pcs_and_mark_sea_in_filled_rows_and_cols(board, ship)
    return True


def get_potential_ships_for_ship_piece_position(
    board: Board,
    x: int,
    y: int,
    ship_length: int
) -> List[Ship]:
    """Returns a list of ships of length ship_length that can each potentially
    be placed onto the board so that one ship piece occupies the board field
    at coordinates (x, y).

    board - The board onto which to check ship placement.
    x - Board playfield field row index.
    y - Board playfield field column index.
    ship_length - The required ship length.
    """
    ships = []  # type: List[Ship]
    if ship_length <= board.rem_pcs_in_rows[x]:
        min_y = max(y - (ship_length - 1), 0)
        max_y = min(y, board.size - 1 - ship_length)
        for i in range(min_y, max_y + 1):
            ship = Ship(x, i, ship_length, Direction.RIGHT)
            if can_fit_ship_on_board(board, ship):
                ships.append(ship)
    if ship_length <= board.rem_pcs_in_cols[y] and ship_length > 1:
        min_x = max(x - (ship_length - 1), 0)
        max_x = min(x, board.size - 1 - ship_length)
        for i in range(min_x, max_x + 1):
            ship = Ship(i, y, ship_length, Direction.DOWN)
            if can_fit_ship_on_board(board, ship):
                ships.append(ship)
    return ships


def get_potential_ships_for_ship_pcs_positions(
    board: Board,
    fleet: Fleet,
    ship_pcs_positions: List[Tuple[int, int]]
) -> Dict[Tuple[int, int], List[Ship]]:
    """Returns a dictionary mapping each field in ship_pcs_positions to a list
    of ships that can each potentially be placed onto the board so that one
    ship piece occupies that particular field.

    board - The board onto which to check ship placement.
    fleet - The fleet of ships yet to be marked onto the board.
    ship_pcs_positions - Coordinates of board fields containing ship pieces.
    """
    potential_ships_for_ship_pcs_positions = {} \
        # type: Dict[Tuple[int, int], List[Ship]]
    for x, y in ship_pcs_positions:
        for ship_length in fleet.ship_lengths:
            if fleet.subfleet_sizes[ship_length] > 0:
                potential_ships_for_ship_pcs_positions[(x, y)] = \
                    potential_ships_for_ship_pcs_positions.get((x, y), []) + \
                    get_potential_ships_for_ship_piece_position(
                        board, x, y, ship_length
                    )
    return potential_ships_for_ship_pcs_positions


def reduce_potential_ships_for_ship_pcs_positions(
    ship_pcs_positions: List[Tuple[int, int]],
    potential_ships_for_ship_pcs_positions: Dict[Tuple[int, int], List[Ship]],
    ship: Ship
) -> None:
    """Removes from potential_ships_for_ship_pcs_positions all occurences of
    'ship'. If after removing there are no other potential ships for given
    coordinates, remove the coordinates and associated empty list from ships
    list for the ship piece coordinates.

    ship_pcs_positions - Coordinates of board fields containing ship pieces.
    potential_ships_for_ship_pcs_positions - Dictionary mapping each field in
        ship_pcs_positions to a list of ships that can each potentially be
        placed onto the board so that one ship piece occupies that particular
        field.
    ship - The ship to validate potential_ships_for_ship_pcs_positions against.
    """
    for x, y in ship_pcs_positions:
        if (
            (ship.direction == Direction.RIGHT and x == ship.x and
                ship.y <= y < ship.y + ship.length) or
            (ship.direction == Direction.DOWN and y == ship.y and
                ship.x <= x < ship.x + ship.length)
        ):
            potential_ships_for_ship_pcs_positions[(x, y)].remove(ship)
            if len(potential_ships_for_ship_pcs_positions[(x, y)]) == 0:
                del(potential_ships_for_ship_pcs_positions[(x, y)])


def mark_uncovered_ships(
    board: Board,
    fleet: Fleet,
    ship_pcs_positions: List[Tuple[int, int]],
    potential_ships_for_ship_pcs_positions: Dict[Tuple[int, int], List[Ship]]
) -> None:
    """Marks ships onto board on those coordinates on which only one ship from
    potential_ships_for_ship_pcs_positions can be placed and updates fleet
    accordingly.

    board - The board onto which to mark ships.
    fleet - The fleet of ships yet to be marked onto the board.
    ship_pcs_positions - Coordinates of board fields containing ship pieces.
    potential_ships_for_ship_pcs_positions - Dictionary of potential ships
        which can be placed on a particular field containing any ship piece.
    """
    for x, y in ship_pcs_positions:
        if len(potential_ships_for_ship_pcs_positions[(x, y)]) == 1:
            ship = potential_ships_for_ship_pcs_positions[(x, y)][0]
            mark_ships(board, fleet, [ship])
            reduce_potential_ships_for_ship_pcs_positions(
                ship_pcs_positions, potential_ships_for_ship_pcs_positions,
                ship
            )


def get_potential_ships_of_length(
    board: Board,
    ship_length: int
) -> List[Ship]:
    """Returns a list of all possible ships of length ship_length which can be
    placed onto any board field.

    board - The board against which to check ship placement.
    ship_length - Length of ship.
    """
    potential_subfleet_ship_positions = []  # type: List[Ship]
    for row in range(1, board.size - 1):
        for col in range(1, board.size - 1):
            if board.playfield[row][col] == FieldType.UNKNOWN:
                if (
                    ship_length <= board.rem_pcs_in_rows[row] and
                    col + ship_length < board.size
                ):
                    ship = Ship(row, col, ship_length, Direction.RIGHT)
                    if can_fit_ship_on_board(board, ship):
                        potential_subfleet_ship_positions.append(ship)
                if (
                    ship_length <= board.rem_pcs_in_cols[col] and
                    row + ship_length < board.size and
                    ship_length > 1
                ):
                    ship = Ship(row, col, ship_length, Direction.DOWN)
                    if can_fit_ship_on_board(board, ship):
                        potential_subfleet_ship_positions.append(ship)
    return potential_subfleet_ship_positions


def find_and_add_solutions(
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
            find_and_add_solutions(board, fleet, subfleet_index + 1, solutions)
        else:
            solutions.append(board)
    else:
        potential_ships = get_potential_ships_of_length(
            board, fleet.ship_lengths[subfleet_index]
        )
        if len(potential_ships) == subfleet_size:
            new_board, new_fleet = board.get_copy(), fleet.get_copy()
            if mark_ships(new_board, new_fleet, potential_ships):
                if subfleet_index + 1 < len(fleet.ship_lengths):
                    find_and_add_solutions(
                        new_board, new_fleet, subfleet_index + 1, solutions
                    )
                else:
                    solutions.append(new_board)
        else:
            if 'combinations' not in sys.modules:
                from itertools import combinations
            for ship_combination in combinations(
                potential_ships, subfleet_size
            ):
                new_board, new_fleet = board.get_copy(), fleet.get_copy()
                if mark_ships(new_board, new_fleet, ship_combination):
                    if subfleet_index + 1 < len(fleet.ship_lengths):
                        find_and_add_solutions(
                            new_board, new_fleet, subfleet_index + 1, solutions
                        )
                    else:
                        solutions.append(new_board)


def get_solutions(
    board: Board,
    fleet: Fleet,
    potential_ships_for_ship_pcs_positions: Dict[Tuple[int, int], List[Ship]]
) -> List[Board]:
    """Returns a list of solutions for given board, given fleet and given list
    of potential ships that occupy board positions where ship pieces are
    located.

    board - Board for which to find solutions.
    fleet - Fleet of ships to be marked onto the board.
    potential_ships_for_ship_pcs_positions - Dictionary of potential ships that
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
            combination_fleet_sizes[ship.length] = (
                combination_fleet_sizes.get(ship.length, 0) + 1
            )
            if (
                combination_fleet_sizes[ship.length] >
                    fleet.subfleet_sizes[ship.length]
            ):
                return True
        return False

    solutions = []  # type: List[Board]
    if len(potential_ships_for_ship_pcs_positions) == 0:
        find_and_add_solutions(board, fleet, 0, solutions)
    else:
        from itertools import product
        for ship_combination in product(
            *potential_ships_for_ship_pcs_positions.values()
        ):
            ship_combination = set(ship_combination)
            if not ship_combination_exceeds_fleet(fleet, ship_combination):
                new_board, new_fleet = board.get_copy(), fleet.get_copy()
                if mark_ships(new_board, new_fleet, ship_combination):
                    find_and_add_solutions(new_board, new_fleet, 0, solutions)
    return solutions


def get_solutions_for_input_file(input_file_uri: str) -> List[Board]:
    """Returns a list of solutions for input parameters given in the file at
    location 'input_file_uri'.

    input_file_uri - URI of file containing board and fleet data.
    """
    global FieldType
    FieldType = get_redefined_FieldType_from_ini_file('../Battleships.ini')
    board_size, playfield, solution_pcs_in_rows, solution_pcs_in_cols, \
        fleet = get_data_from_file(input_file_uri)
    board = get_board_from_input_data(
        board_size, playfield, solution_pcs_in_rows, solution_pcs_in_cols
    )
    ship_pcs_positions = get_ship_pcs_positions(board)
    mark_uncovered_sea_positions(board, ship_pcs_positions)
    for x, y in ship_pcs_positions:
        board.playfield[x][y] = FieldType.UNKNOWN
    potential_ships_for_ship_pcs_positions = \
        get_potential_ships_for_ship_pcs_positions(
            board, fleet, ship_pcs_positions
        )
    mark_uncovered_ships(
        board, fleet, ship_pcs_positions,
        potential_ships_for_ship_pcs_positions
    )
    return get_solutions(board, fleet, potential_ships_for_ship_pcs_positions)


def main(input_file_uri: str) -> None:
    """Main function. Defined separately for diagnostic purposes.

    input_file_uri - URI of file containing board and fleet data
    """
    solutions = get_solutions_for_input_file(input_file_uri)
    for solution in solutions:
        print(solution.repr(True))
    if solutions:
        print("{} solutions in total.".format(len(solutions)))


if __name__ == "__main__":
    main('../tests/board_samples/board02.txt')
