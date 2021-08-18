"""Contains data structured for managing a 2-dimensional grid of
FieldType elements.
"""

import collections
import enum
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Set

import params


class FieldType(enum.Enum):
    """Types of fields."""

    SEA = params.FIELDTYPE_SYMBOLS.SEA
    SHIP = params.FIELDTYPE_SYMBOLS.SHIP
    UNKNOWN = params.FIELDTYPE_SYMBOLS.UNKNOWN


class Position(NamedTuple):
    """Grid field coordinates."""

    row: int
    col: int


class Series(enum.Enum):
    """Two basic ways of spatial distribution of elements."""

    ROW = "ROW"
    COLUMN = "COLUMN"

    def __repr__(self) -> str:
        """Get a string representation of self.

        Returns:
            str: String representation of self.

        """
        return f"<{self.__class__.__name__}.{self.name}>"


if TYPE_CHECKING:
    MyUserList = collections.UserList[List[FieldType]]  # pylint: disable=C0103
else:
    MyUserList = collections.UserList


class FieldTypeGrid(MyUserList):
    """A 2-dimensional grid of elements of type FieldType."""

    def __repr__(self) -> str:
        """Get a string representation of self.

        Returns:
            str: String representation of self.

        """
        ret_val = ""
        for row in self:
            row_repr = "".join(" " + field.value + "  " for field in row[:-1])
            row_repr += " " + row[-1].value + " \n"
            ret_val += row_repr
        return ret_val.strip("\n")

    def get_series(
        self,
        series: Series,
        series_index: int,
        complementary_series_slice: Optional[slice] = None,
    ) -> List[FieldType]:
        """Get a full or partial series of grid fields.

        While the series parameter determines the series to get, the
        complementary_series_slice parameter limits the series to the
        slice range.

        Args:
            series (battleships.grid.Series): Grid series type.
            series_index (int): Index of series within the grid.
            complementary_series_slice (slice): Slice to apply to the
                series.

        Returns:
            List[battleships.grid.FieldType]: Series of FieldType grid
                fields.

        Raises:
            battleships.grid.InvalidSeriesException: When an invalid
                grid series is referenced.

        """
        if complementary_series_slice:
            series_count = {
                Series.ROW: self[series_index][complementary_series_slice],
                Series.COLUMN: [
                    row[series_index] for row in self[complementary_series_slice]
                ],
            }
        else:
            series_count = {
                Series.ROW: self[series_index],
                Series.COLUMN: [row[series_index] for row in self],
            }
        return series_count[series]

    def fieldtype_count_in_series(
        self,
        fieldtype: FieldType,
        series: Series,
        series_index: int,
        complementary_series_slice: Optional[slice] = None,
    ) -> int:
        """Get count of fields of selected FieldType in a series of grid
        fields.

        Args:
            fieldtype (battleships.grid.FieldType): Selected type of
                FieldTypes.
            series (battleships.grid.Series): Grid series type.
            series_index (int): Index of series in the grid.
            complementary_series_slice (slice): Slice to apply to the
                series.

        Returns:
            int: Count of fieldtypes in the selected series.

        """
        return self.get_series(series, series_index, complementary_series_slice).count(
            fieldtype
        )

    def fieldtype_positions_in_series(
        self, fieldtype: FieldType, series: Series, series_index: int
    ) -> Set[Position]:
        """Get positions of fields of selected type in a series of grid
        fields.

        Args:
            fieldtype (battleships.grid.FieldType): Selected FieldTypes
                type.
            series (battleships.grid.Series): Grid series type.
            series_index (int): Index of series within the grid.

        Returns:
            Set[battleships.grid.Position]: Set of positions of fields
                of given fieldtype.

        """
        positions_for_series = {
            Series.ROW: {
                Position(series_index, col)
                for col, field in enumerate(self[series_index])
                if field == fieldtype
            },
            Series.COLUMN: {
                Position(row_index, series_index)
                for row_index, row in enumerate(self)
                if row[series_index] == fieldtype
            },
        }
        return positions_for_series[series]

    def replace_fields_in_series(
        self,
        fieldtype_old: FieldType,
        fieldtype_new: FieldType,
        series: Series,
        series_index: int,
    ) -> None:
        """Replace one FieldType in a series with another fieldtype.

        Args:
            fieldtype_old (battleships.grid.FieldType): Type of
                FieldType to replace.
            fieldtype_new (battleships.grid.FieldType): Type of
                FieldType with which to replace.
            series (battleships.grid.Series): Grid series type.
            series_index (int): Index of series within the grid.
        """

        def replace_in_row(row_index: int) -> None:
            self[row_index] = [
                fieldtype_new if field == fieldtype_old else field
                for field in self[row_index]
            ]

        def replace_in_column(column_index: int) -> None:
            for row in self:
                if row[column_index] == fieldtype_old:
                    row[column_index] = fieldtype_new

        fn_to_call_for_series = {
            Series.ROW: replace_in_row,
            Series.COLUMN: replace_in_column,
        }
        fn_to_call_for_series[series](series_index)


class InvalidSeriesException(Exception):
    """Raised when an invalid FieldTypeGrid series is referenced."""
