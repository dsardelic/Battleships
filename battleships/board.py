"""This module contains data structures for managing board data."""

import functools
import itertools
from typing import Any, DefaultDict, Dict, Iterable, List, Set

from battleships.grid import FieldType, FieldTypeGrid, Position, Series
from battleships.ship import Ship


class Board:
    """Represents a puzzle board object.
    
    A board is a numbered grid of FieldType elements. Each number
    indicates how many ship fields remain to be marked in the
    corresponding row or column.
    
    In order to ease grid index checks and marking of ships near grid
    edges, the grid is extended with a sea field rim. Therefore, the
    resulting grid is 2 rows and 2 columns bigger than the input grid.

    Class instance attributes:
        grid (battleships.grid.FieldTypeGrid): Grid of FieldType
            elements.
        number_of_ship_fields_to_mark_in_series (Dict[
            battleships.grid.Series, List[int]]): For each Series type
            indicates how many ship fields remain to be marked in the
            corresponding series.
    """

    __slots__ = ("grid", "number_of_ship_fields_to_mark_in_series")

    def __init__(
        self,
        grid: FieldTypeGrid,
        number_of_ship_fields_to_mark_in_series: Dict[Series, List[int]],
    ) -> None:
        """Initialize a new Board object.
        
        Args:
            grid (battleships.grid.FieldTypeGrid): Grid of FieldType
                elements.
            number_of_ship_fields_to_mark_in_series
                (Dict[battleships.grid.Series, List[int]]):
                For each Series type indicates how many ship fields
                remain to be marked in the corresponding series.
        """
        self.grid = grid
        self.number_of_ship_fields_to_mark_in_series = (
            number_of_ship_fields_to_mark_in_series
        )

    def __repr__(self) -> str:
        """Return a string representation of self.
        
        Returns:
            str: String representation of self.
        
        """
        return self.repr(True)

    def __eq__(self, other: Any) -> bool:
        """Compare self with some other object.
        
        Args:
            other: The object to compare with self.
        
        Returns:
            bool: True if objects are equal, False otherwise.
        """
        if isinstance(other, self.__class__):
            return (
                other.grid == self.grid
                and other.number_of_ship_fields_to_mark_in_series
                == self.number_of_ship_fields_to_mark_in_series
            )
        return False

    @classmethod
    def parse_board(
        cls,
        grid: FieldTypeGrid,
        number_of_ship_fields_to_mark_in_rows: List[int],
        number_of_ship_fields_to_mark_in_cols: List[int],
    ) -> "Board":
        """Create a Board object from original board data.
        
        Unlike Board object data, original board data correspond to what
        a person solving the puzzle on paper would see.
        
        Args:
            grid (battleships.grid.FieldTypeGrid): Input grid of
                FieldType elements.
            number_of_ship_fields_to_mark_in_rows (List[int]): List of
                numbers of ship fields to mark in each corresponding
                input grid row.
            number_of_ship_fields_to_mark_in_cols (List[int]): List of
                numbers of ship fields to mark in each corresponding
                input grid column.
        
        Returns:
            battleships.board.Board: Board object created from original
                board data.
        
        """
        board_size = len(number_of_ship_fields_to_mark_in_rows) + 2
        board_grid = FieldTypeGrid()  # type: FieldTypeGrid
        board_grid.append([FieldType.SEA] * board_size)
        board_grid += [[FieldType.SEA, *grid_row, FieldType.SEA] for grid_row in grid]
        board_grid.append([FieldType.SEA] * board_size)
        board_number_of_ship_fields_to_mark_in_series = {
            Series.ROW: [0, *number_of_ship_fields_to_mark_in_rows, 0],
            Series.COLUMN: [0, *number_of_ship_fields_to_mark_in_cols, 0],
        }
        for row_index, row in enumerate(grid, 1):
            for col_index, field in enumerate(row, 1):
                if field == FieldType.SHIP:
                    board_number_of_ship_fields_to_mark_in_series[Series.ROW][
                        row_index
                    ] -= 1
                    board_number_of_ship_fields_to_mark_in_series[Series.COLUMN][
                        col_index
                    ] -= 1
        return Board(board_grid, board_number_of_ship_fields_to_mark_in_series)

    @classmethod
    def get_copy_of(cls, original_board: "Board") -> "Board":
        """Create a copy of a Board object.
        
        Args:
            original_board (battleships.board.Board): The board to copy.
        
        Returns:
            battleships.board.Board: A copy of the input Board object.
        
        """
        board_copy_grid = FieldTypeGrid([[*row] for row in original_board.grid])
        board_copy_number_of_ship_fields_to_mark_in_series = {
            Series.ROW: [
                *original_board.number_of_ship_fields_to_mark_in_series[Series.ROW]
            ],
            Series.COLUMN: [
                *original_board.number_of_ship_fields_to_mark_in_series[Series.COLUMN]
            ],
        }
        return cls(board_copy_grid, board_copy_number_of_ship_fields_to_mark_in_series)

    @property
    def size(self) -> int:
        """Return size of self's grid.
        
        The grid is expected to be square-shaped, thus both dimensions
            have the same size.
        
        Returns:
            int: Size of self's grid.
        
        """
        return len(self.grid)

    def repr(self, with_ship_fields_to_mark_count: bool) -> str:
        """Return a string representation of self.
        
        Args:
            with_ship_fields_to_mark_count (bool): True if number of
                ship fields to mark in each row and column is to be
                included in the representation, False otherwise.
        
        Returns:
            str: String representation of self.
        
        """
        grid = FieldTypeGrid(
            [row[1 : self.size - 1] for row in self.grid[1 : self.size - 1]]
        )
        top_frame_border = (
            "\u2554\u2550" + "\u2550\u2550\u2550\u2550" * (self.size - 2) + "\u2557\n"
        )
        fieldtype_rows = ""
        for row_index, grid_row_repr in enumerate(repr(grid).split("\n"), 1):
            row_rep = "".join(["\u2551 ", grid_row_repr.strip("\n"), " \u2551"])
            if with_ship_fields_to_mark_count:
                row_rep += "".join(
                    [
                        "(",
                        str(
                            self.number_of_ship_fields_to_mark_in_series[Series.ROW][
                                row_index
                            ]
                        ),
                        ")",
                    ]
                )
            fieldtype_rows += row_rep + "\n"
        bottom_frame_border = (
            "\u255A\u2550" + "\u2550\u2550\u2550\u2550" * (self.size - 2) + "\u255D\n"
        )
        ret_val = "".join([top_frame_border, fieldtype_rows, bottom_frame_border])

        if with_ship_fields_to_mark_count:
            ret_val += (
                "  "
                + "".join(
                    "(" + str(x) + ") "
                    for x in self.number_of_ship_fields_to_mark_in_series[
                        Series.COLUMN
                    ][1 : self.size - 1]
                )
                + "\n"
            )
        return ret_val.strip("\n")

    def set_ship_fields_as_unknown(self, ship_fields_positions: Set[Position]) -> None:
        """Mark current FieldType as unknown on all given ship positions
        in self's grid.
        
        Args:
            ship_fields_positions (Set[battleships.grid.Position]):
                Positions of which to perform the field type
                replacement.
        
        """
        for position in ship_fields_positions:
            self.grid[position.row][position.col] = FieldType.UNKNOWN
            self.number_of_ship_fields_to_mark_in_series[Series.ROW][position.row] += 1
            self.number_of_ship_fields_to_mark_in_series[Series.COLUMN][
                position.col
            ] += 1

    def get_ship_fields_positions(self) -> Set[Position]:
        """Get all self's grid positions containing ship fields.
        
        Returns:
            Set[battleships.grid.Position]: Set of self's grid positions
                containing ship fields.
        
        """
        return functools.reduce(
            set.union,
            [
                self.grid.fieldtype_positions_in_series(
                    FieldType.SHIP, Series.ROW, row_index
                )
                for row_index in range(1, self.size - 1)
            ],
        )

    def mark_sea_in_series_with_no_rem_ship_fields(self) -> None:
        """In those series where there are no more ship fields to be
        marked in self's grid, replace unknown fields with sea fields.
        """
        for series in Series:
            for series_index in range(1, self.size - 1):
                if not self.number_of_ship_fields_to_mark_in_series[series][
                    series_index
                ]:
                    self.grid.replace_fields_in_series(
                        FieldType.UNKNOWN, FieldType.SEA, series, series_index
                    )

    def mark_diagonal_sea_fields_for_positions(
        self, ship_fields_positions: Set[Position]
    ) -> None:
        """Mark sea fields in all self's grid's positions diagonal to
        given positions.
        
        While another potential ship piece might be found right next to
        a particular position (in the same row or column), all positions
        diagonal to the given position cannot contain anything other
        than sea fields.
        
        Args:
            ship_fields_positions (Set[battleships.grid.Position]):
                Positions for which to mark sea fields on diagonal
                positions.
        
        """
        for position in ship_fields_positions:
            for offset_row, offset_col in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                self.grid[position.row + offset_row][
                    position.col + offset_col
                ] = FieldType.SEA

    def ship_is_within_playable_grid(self, ship: Ship) -> bool:
        """Check whether ship is within self's grid playable part.
        
        Playable grid part is the board grid without the surrounding sea
        fields extension.
        
        Args:
            ship (battleships.ship.Ship): Ship whose placement to check.
        
        Returns:
            bool: True is ship is within self's grid's playable part,
                False otherwise.
        
        """
        return (
            ship.position.row > 0
            and ship.position.col > 0
            and all(
                ship.max_ship_field_index_in_series[series] < self.size - 1
                for series in Series
            )
        )

    def sufficient_remaining_ship_fields_to_mark_ship(self, ship: Ship) -> bool:
        """Check whether there are enough remaining ship fields to mark
        a ship onto self's grid.
        
        The check is run for rows and columns that the ship would
        occupy.
        
        Args:
            ship (battleships.ship.Ship): Ship whose potential placement
                to check.
        
        Returns:
            bool: True if there are sufficient remaining ship fields to
                mark ship onto self's grid, False otherwise.
        
        """
        return all(
            self.number_of_ship_fields_to_mark_in_series[series][series_index]
            >= ship.ship_fields_count_in_series[series]
            for series in Series
            for series_index in ship.ship_fields_range[series]
        )

    def no_disallowed_overlapping_fields_for_ship(self, ship: Ship) -> bool:
        """Check whether ship marking onto self's grid would result in
        disallowed field overlaps.
        
        The check takes into consideration the entire ship's zone of
        control.
        
        Args:
            ship (battleships.ship.Ship): Ship whose potential placement
                to check.
        
        Returns:
            bool: True if no disallowed overlappings would occur by
                marking the ship, False otherwise.
        
        """
        return all(
            board_field == FieldType.UNKNOWN
            or (board_field == FieldType.SEA and ship_field == FieldType.SEA)
            for board_row, ship_row in zip(
                self.grid[ship.zoc_slice[Series.ROW]], ship.grid
            )
            for board_field, ship_field in zip(
                board_row[ship.zoc_slice[Series.COLUMN]], ship_row
            )
        )

    def can_fit_ship(self, ship: Ship) -> bool:
        """Check if ship fits onto self's grid.
        
        Args:
            ship (battleships.ship.Ship): Ship whose placement to check.
        
        Returns:
            bool: True if ship fits onto self's grid, False otherwise.
        
        """
        return all(
            (
                self.ship_is_within_playable_grid(ship),
                self.sufficient_remaining_ship_fields_to_mark_ship(ship),
                self.no_disallowed_overlapping_fields_for_ship(ship),
            )
        )

    def mark_ship_group(self, ships_to_mark: Iterable[Ship]) -> None:
        """Simulate marking of a group of ships onto self's grid.
        
        Args:
            ships_to_mark (Iterable[battleships.ship.Ship]): Ships to
                mark onto self's grid.
        
        Raises:
            battleships.board.InvalidShipPlacementException: If the
                ships to mark cannot all at the same time be placed onto
                self's grid.
        
        """
        for ship_to_mark in ships_to_mark:
            if self.can_fit_ship(ship_to_mark):
                self.mark_ship_and_surrounding_sea(ship_to_mark)
                self.mark_sea_in_series_with_no_rem_ship_fields()
            else:
                raise InvalidShipPlacementException

    def find_definite_ship_fields_positions(self) -> Set[Position]:
        """Find a set of self's grid positions that definitely contain
        ship fields.
        
        Definite ship fields can be determined by comparing the number
        of ship fields remaining to be marked in a series to the number
        of unknown fields in that same series. If the numbers are equal,
        then all unknown fields are definitely ship fields.
        
        The algorithm keeps track of all newly detected definite ship
        fields, as well as marks all newly discovered sea fields.
        
        The discovery procedure is repeated until no new definite ship
        fields are found.
        
        Returns:
            Set[battleships.grid.Position]: Self's grid positions which
                are determined to definitely contain ship fields.
        
        """
        ship_fields_to_be = set()  # type: Set[Position]
        board_to_be = Board.get_copy_of(self)
        continue_searching = True
        while continue_searching:
            continue_searching = False
            ship_fields_to_be_new = set()  # type: Set[Position]
            for series, series_index in itertools.product(
                Series, range(1, board_to_be.size - 1)
            ):
                ship_fields_to_mark_count, unknown_fields_count = (
                    board_to_be.number_of_ship_fields_to_mark_in_series[series][
                        series_index
                    ],
                    board_to_be.grid.fieldtype_count_in_series(
                        FieldType.UNKNOWN, series, series_index
                    ),
                )
                if (
                    ship_fields_to_mark_count > 0
                    and ship_fields_to_mark_count == unknown_fields_count
                ):
                    continue_searching = True
                    unknown_positions = board_to_be.grid.fieldtype_positions_in_series(
                        FieldType.UNKNOWN, series, series_index
                    )
                    ship_fields_to_be_new.update(unknown_positions)
            for position in ship_fields_to_be_new:
                board_to_be.grid[position.row][position.col] = FieldType.SHIP
                board_to_be.mark_diagonal_sea_fields_for_positions({position})
                board_to_be.number_of_ship_fields_to_mark_in_series[Series.ROW][
                    position.row
                ] -= 1
                board_to_be.number_of_ship_fields_to_mark_in_series[Series.COLUMN][
                    position.col
                ] -= 1
            board_to_be.mark_sea_in_series_with_no_rem_ship_fields()
            ship_fields_to_be.update(ship_fields_to_be_new)
        return ship_fields_to_be

    def get_possible_ships_occupying_positions(
        self, positions: Set[Position], ship_sizes: Iterable[int]
    ) -> Dict[Position, Set[Ship]]:
        """For each given position in self's grid determine a set of
        ships whose ship fields might - one at a time - cover that
        position.
        
        Args:
            positions (Set[battleships.grid.Position]): Board positions
                that are to be covered.
            ship_sizes (Iterable[int]): Allowed sizes of ships to cover
                the board positions.
        
        Returns:
            Dict[battleships.grid.Position, Set[battleships.ship.Ship]]:
                For each position a set of ships whose ship fields might
                - one at a time - cover that position.
        
        """
        ships_occupying_positions = DefaultDict(
            set
        )  # type: DefaultDict[Position, Set[Ship]]
        for ship_size in [ship_size for ship_size in ship_sizes if ship_size != 1]:
            for position in positions:
                possible_ship_positions_for_orientation = {
                    Series.ROW: (
                        Position(position.row, col_index)
                        for col_index in range(
                            max(position.col - (ship_size - 1), 1),
                            min(position.col, self.size - 1 - ship_size) + 1,
                        )
                    ),
                    Series.COLUMN: (
                        Position(row_index, position.col)
                        for row_index in range(
                            max(position.row - (ship_size - 1), 1),
                            min(position.row, self.size - 1 - ship_size) + 1,
                        )
                    ),
                }
                ships_occupying_positions[position].update(
                    {
                        Ship(position, ship_size, orientation)
                        for orientation in Series
                        for position in possible_ship_positions_for_orientation[
                            orientation
                        ]
                        if self.can_fit_ship(Ship(position, ship_size, orientation))
                    }
                )
        if 1 in ship_sizes:
            for position in positions:
                ships_occupying_positions[position].update(
                    {Ship(position, 1, Series.ROW)}
                )
        return ships_occupying_positions

    def get_possible_ships_of_size(self, size: int) -> Set[Ship]:
        """Get all possible ships of a given size that can - one at a
        time - be placed anywhere on self's grid.
        
        Args:
            size (int): Size of ship i.e. number of ship fields it
                contains.
        
        Returns:
            Set[battleships.ship.Ship]: Ships of given size that can -
                one at a time - be placed onto self's grid.
        
        """
        if size == 1:
            return {
                Ship(Position(row_index, col_index), size, Series.ROW)
                for row_index, row in enumerate(self.grid[1 : self.size - 1], 1)
                for col_index, field in enumerate(row[1 : self.size - 1], 1)
                if field == FieldType.UNKNOWN
                and self.can_fit_ship(
                    Ship(Position(row_index, col_index), size, Series.ROW)
                )
            }
        return {
            Ship(Position(row_index, col_index), size, orientation)
            for row_index, row in enumerate(self.grid[1 : self.size - 1], 1)
            for col_index, field in enumerate(row[1 : self.size - 1], 1)
            for orientation in Series
            if field == FieldType.UNKNOWN
            and self.can_fit_ship(
                Ship(Position(row_index, col_index), size, orientation)
            )
        }

    def mark_ship_and_surrounding_sea(self, ship: Ship) -> None:
        """Mark ship and its surrounding sea onto self's grid.
        
        Args:
            ship (battleships.ship.Ship): Ship to mark onto self's grid.
        
        """
        for ship_row_index, board_row in enumerate(
            self.grid[ship.zoc_slice[Series.ROW]]
        ):
            board_row[ship.zoc_slice[Series.COLUMN]] = ship.grid[ship_row_index]
        for series in Series:
            self.number_of_ship_fields_to_mark_in_series[series][
                ship.ship_fields_slice[series]
            ] = [
                x - ship.ship_fields_count_in_series[series]
                for x in self.number_of_ship_fields_to_mark_in_series[series][
                    ship.ship_fields_slice[series]
                ]
            ]

    def is_overmarked(self) -> bool:
        """Check whether the number of ship fields to mark in any self's
        grid series is bigger than the number of available unknown
        fields in that same series.
        
        Returns:
            bool: True if the number of ship fields to mark in any
                self's grid series is bigger than the number of
                available unknown fields in that same series, False
                otherwise.
        
        """
        return any(
            self.number_of_ship_fields_to_mark_in_series[series][series_index]
            > self.grid.fieldtype_count_in_series(
                FieldType.UNKNOWN, series, series_index
            )
            for series in Series
            for series_index in range(1, self.size - 1)
        )


class InvalidShipPlacementException(Exception):
    """Raised when ship's placement onto the board is invalid."""
