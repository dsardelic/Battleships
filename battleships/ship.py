"""This module contains data structures for managing ship data."""

import dataclasses
from typing import Any, Callable, Dict, Tuple, TypeVar

from battleships.grid import FieldType, FieldTypeGrid, Position, Series

GenericType = TypeVar("GenericType")


class ShipGrid(FieldTypeGrid):
    """Acts as a storage of grids corresponding to possible ship
    types.
    """

    ShipGridMappings = Dict[Tuple[int, Series], FieldTypeGrid]

    _grids = {}  # type: ShipGridMappings

    @classmethod
    def get_grid(cls, ship_size: int, orientation: Series) -> FieldTypeGrid:
        """Get grid of a ship of particular size and orientation.
        
        Args:
            ship_size (int): Size of ship.
            orientation (battleships.grid.Series): Ship orientation.
        
        Returns:
            battleships.grid.FieldTypeGrid: Grid of ship of given size
                and orientation.
        
        """

        def generate_grid(ship_size: int, orientation: Series) -> FieldTypeGrid:
            def generate_grid_with_row_orientation(ship_size: int) -> FieldTypeGrid:
                grid = FieldTypeGrid()
                grid.append([FieldType.SEA] * (ship_size + 2))
                grid.append(
                    [FieldType.SEA] + [FieldType.SHIP] * ship_size + [FieldType.SEA]
                )
                grid.append([FieldType.SEA] * (ship_size + 2))
                return grid

            def generate_grid_with_column_orientation(ship_size: int) -> FieldTypeGrid:
                grid = FieldTypeGrid()
                grid.append([FieldType.SEA] * 3)
                grid += [
                    [FieldType.SEA, FieldType.SHIP, FieldType.SEA]
                    for _ in range(ship_size)
                ]
                grid.append([FieldType.SEA] * 3)
                return grid

            if orientation == Series.ROW:
                return generate_grid_with_row_orientation(ship_size)
            return generate_grid_with_column_orientation(ship_size)

        grid = cls._grids.get((ship_size, orientation), None)
        if grid:
            return grid
        cls._grids[(ship_size, orientation)] = generate_grid(ship_size, orientation)
        return cls._grids[(ship_size, orientation)]


@dataclasses.dataclass(unsafe_hash=True)
class Ship:
    """Class representing a ship.
    
    A ship is unequivocally determined by its attributes:
        1) Position on the grid (battleships.grid.Position) -
            coordinates of the ship field nearest to the position (0, 0)
        2) Size (int) - number of ship fields
        3) Orientation (battleships.grid.Series) - direction in which
            the ship fields are spatially distributed on the grid.
    
    A ship of size 1 should be initialized with Series.ROW orientation.
    
    The ship itself includes fields of type FieldType.SHIP only. The
    area containing sea fields around the ship is referred to as ship's
    "zone of control" or ZOC. As per puzzle rules, two or more ships
    may share one or more fields in their respective ZOCs.
    """

    position: Position
    size: int
    orientation: Series

    def __init__(self, position: Position, size: int, orientation: Series):
        """Initialize a new Ship object.
        
        Args:
           position (Position): Ship's position on the grid.
           size (int): Ship's size.
           orientation (Series): Ship's orientation.
         
        """
        self.position = position
        self.size = size
        self.orientation = orientation

        """The following "private" attributes are used for optimization
        purposes. They enable the actual class properties to behave
        "lazily" and to store the property value once it is calculated.
        """
        self._ship_fields_count_in_series = {}  # type: Dict[Series, int]
        self._max_ship_field_index_in_series = {}  # type: Dict[Series, int]
        self._ship_fields_range = {}  # type: Dict[Series, range]
        self._ship_fields_slice = {}  # type: Dict[Series, slice]
        self._zoc_slice = {}  # type: Dict[Series, slice]

    @property
    def grid(self) -> FieldTypeGrid:
        """Return FieldTypeGrid object which corresponds to this ship.
        
        Returns:
            battleships.grid.FieldTypeGrid: FieldTypeGrid which
                corresponds to this ship.
        
        """
        return ShipGrid.get_grid(self.size, self.orientation)

    @property
    def ship_fields_count_in_series(self) -> Dict[Series, int]:
        """Get number of ship fields in each possible orientation.
        
        Returns:
            Dict[battleships.grid.Series, int]: Number of ship fields
                per grid series.
        
        """
        if not self._ship_fields_count_in_series:
            self._ship_fields_count_in_series = {
                Series.ROW: {Series.ROW: self.size, Series.COLUMN: 1},
                Series.COLUMN: {Series.ROW: 1, Series.COLUMN: self.size},
            }[self.orientation]
        return self._ship_fields_count_in_series

    @property
    def max_ship_field_index_in_series(self) -> Dict[Series, int]:
        """Get the maximum index of series (per series) which contains a
        piece of this ship.
        
        Returns:
            Dict[battleships.grid.Series, int]: Maximum ship field index
                per grid series.
        
        """
        if not self._max_ship_field_index_in_series:
            self._max_ship_field_index_in_series = {
                Series.ROW: {
                    Series.ROW: self.position.row,
                    Series.COLUMN: self.position.col + self.size - 1,
                },
                Series.COLUMN: {
                    Series.ROW: self.position.row + self.size - 1,
                    Series.COLUMN: self.position.col,
                },
            }[self.orientation]
        return self._max_ship_field_index_in_series

    def _create_reach_object(
        self, function: Callable[..., GenericType], zoc: bool
    ) -> Dict[Series, Any]:
        """Map each series to a "reach object" (range or slice) that
        covers ship fields area or ship ZOC area.
        
        Args:
            function (Callable[..., GenericType]): Either range or slice
                built-in function
            zoc (bool): Indicates whether the reach object covers the
                ship fields or the ship ZOC area
        
        Returns:
            Dict[battleships.grid.Series, Any]: Reach object covering
                ship fields area or ship ZOC area per series.
        
        """

        def reach_limits(min_value: int, max_value: int, zoc: bool) -> Tuple[int, int]:
            if zoc:
                return (min_value - 1, max_value + 1)
            return (min_value, max_value)

        limits_by_series = {
            Series.ROW: {
                Series.ROW: reach_limits(self.position.row, self.position.row + 1, zoc),
                Series.COLUMN: reach_limits(
                    self.position.col, self.position.col + self.size, zoc
                ),
            },
            Series.COLUMN: {
                Series.ROW: reach_limits(
                    self.position.row, self.position.row + self.size, zoc
                ),
                Series.COLUMN: reach_limits(
                    self.position.col, self.position.col + 1, zoc
                ),
            },
        }[self.orientation]

        return {
            series: function(*limits) for series, limits in limits_by_series.items()
        }

    @property
    def ship_fields_range(self) -> Dict[Series, range]:
        """Get ranges of ship fields per series.
        
        Returns:
            Dict[battleships.grid.Series, range]: Ranges of ship fields
                per series.
        
        """
        if not self._ship_fields_range:
            self._ship_fields_range = self._create_reach_object(range, False)
        return self._ship_fields_range

    @property
    def ship_fields_slice(self) -> Dict[Series, slice]:
        """Get slices of ship fields per series.
        
        Returns:
            Dict[battleships.grid.Series, slice]: Slices of ship fields
                per series.
        
        """
        if not self._ship_fields_slice:
            self._ship_fields_slice = self._create_reach_object(slice, False)
        return self._ship_fields_slice

    @property
    def zoc_slice(self) -> Dict[Series, slice]:
        """Get slices of ship ZOC per series.
        
        Returns:
            Dict[battleships.grid.Series, slice]: Slices of ship ZOC per
                series.
        
        """
        if not self._zoc_slice:
            self._zoc_slice = self._create_reach_object(slice, True)
        return self._zoc_slice
