import unittest

from battleships.grid import FieldType, FieldTypeGrid, Position, Series


class TestSeries(unittest.TestCase):
    def test___repr__(self):
        expected_results = ("<Series.ROW>", "<Series.COLUMN>")
        for series, expected_result in zip(Series, expected_results):
            self.assertEqual(expected_result, series.__repr__())


def parse_fieldtypegrid(repr_string):
    return FieldTypeGrid(
        [
            [FieldType(c) for c in row.replace(" ", "")]
            for row in repr_string.strip("\n").split("\n")
        ]
    )


class TestFieldTypeGrid(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sample_fieldtypegrid_reprs = (
            " .   x   . \n"  # dummy comment to counter Black formatting
            " .   x   x \n"
            " .   O   . \n"
            " x   O   . \n"
            " .   .   . ",
            # dummy separator
            " .   x   x   .   .   x \n"
            " .   O   O   x   O   x \n"
            " x   x   .   .   x   . ",
            # dummy separator
            " x   .   x \n"  # dummy comment to counter Black formatting
            " .   O   . \n"
            " .   x   . ",
            # dummy separator
            " .   O   x   O   .   O   .   O \n"
            " O   .   O   .   O   x   O   . \n"
            " .   .   O   O   .   .   O   O \n"
            " O   O   .   .   O   O   .   . \n"
            " .   .   x   x   .   x   .   x \n"
            " x   O   x   O   O   x   O   O ",
        )
        self.sample_fieldtypegrids = (
            parse_fieldtypegrid(fieldtypegrid_repr)
            for fieldtypegrid_repr in self.sample_fieldtypegrid_reprs
        )

    @classmethod
    def fieldtype_vector_from_str(cls, fieldtype_series_str):
        return [FieldType(char) for char in fieldtype_series_str]

    def test___repr__(self):
        for sample_grid, sample_grid_repr in zip(
            self.sample_fieldtypegrids, self.sample_fieldtypegrid_reprs
        ):
            with self.subTest():
                self.assertEqual(sample_grid_repr, sample_grid.__repr__())

    def test_get_series(self):
        params_vector = (
            (Series.ROW, 2),
            (Series.ROW, 2, slice(1, 3)),
            (Series.COLUMN, 2),
            (Series.COLUMN, 2, slice(1, 3)),
        )
        expected_results_vectors = (
            (".O.", "O.", ".x...", "x."),
            ("xx..x.", "x.", "xO.", "O."),
            (".x.", "x.", "x..", ".."),
            ("..OO..OO", ".O", "xOO.xx", "OO"),
        )
        for sample_grid, expected_result_vector in zip(
            self.sample_fieldtypegrids, expected_results_vectors
        ):
            for params, expected_result in zip(params_vector, expected_result_vector):
                with self.subTest():
                    self.assertEqual(
                        TestFieldTypeGrid.fieldtype_vector_from_str(expected_result),
                        sample_grid.get_series(*params),
                    )

    def test_fieldtype_count_in_series(self):
        params_vector = (
            (FieldType.SHIP, Series.ROW, 2),
            (FieldType.SHIP, Series.ROW, 2, slice(1, 3)),
            (FieldType.SHIP, Series.COLUMN, 2),
            (FieldType.SHIP, Series.COLUMN, 2, slice(1, 3)),
        )
        expected_results_vectors = (
            (1, 1, 0, 0),
            (0, 0, 1, 1),
            (0, 0, 0, 0),
            (4, 1, 2, 2),
        )
        for sample_grid, expected_result_vector in zip(
            self.sample_fieldtypegrids, expected_results_vectors
        ):
            for params, expected_result in zip(params_vector, expected_result_vector):
                with self.subTest():
                    self.assertEqual(
                        expected_result, sample_grid.fieldtype_count_in_series(*params)
                    )

    def test_fieldtype_positions_in_series(self):
        params_vector = (
            (FieldType.SHIP, Series.ROW, 2),
            (FieldType.SHIP, Series.COLUMN, 2),
        )
        expected_results_vectors = (
            ({Position(2, 1)}, set()),
            (set(), {Position(1, 2)}),
            (set(), set()),
            (
                {Position(2, 2), Position(2, 3), Position(2, 6), Position(2, 7)},
                {Position(1, 2), Position(2, 2)},
            ),
        )
        for sample_grid, expected_result_vector in zip(
            self.sample_fieldtypegrids, expected_results_vectors
        ):
            for params, expected_result in zip(params_vector, expected_result_vector):
                with self.subTest():
                    self.assertEqual(
                        expected_result,
                        sample_grid.fieldtype_positions_in_series(*params),
                    )

    def test_replace_fields_in_series(self):
        params_vector = (
            (FieldType.SEA, FieldType.UNKNOWN, Series.ROW, 1),
            (FieldType.SEA, FieldType.UNKNOWN, Series.COLUMN, 1),
        )
        expected_grid_repr_vectors = (
            (
                " .   x   . \n"  # dummy comment to counter Black formatting
                " x   x   x \n"
                " .   O   . \n"
                " x   O   . \n"
                " .   .   . ",
                # dummy separator
                " .   x   . \n"  # dummy comment to counter Black formatting
                " .   x   x \n"
                " .   O   . \n"
                " x   O   . \n"
                " .   x   . ",
            ),
            (
                " .   x   x   .   .   x \n"
                " x   O   O   x   O   x \n"
                " x   x   .   .   x   . ",
                # dummy separator
                " .   x   x   .   .   x \n"
                " .   O   O   x   O   x \n"
                " x   x   .   .   x   . ",
            ),
            (
                " x   .   x \n"  # dummy comment to counter Black formatting
                " x   O   x \n"
                " .   x   . ",
                # dummy separator
                " x   x   x \n"  # dummy comment to counter Black formatting
                " .   O   . \n"
                " .   x   . ",
            ),
            (
                " .   O   x   O   .   O   .   O \n"
                " O   x   O   x   O   x   O   x \n"
                " .   .   O   O   .   .   O   O \n"
                " O   O   .   .   O   O   .   . \n"
                " .   .   x   x   .   x   .   x \n"
                " x   O   x   O   O   x   O   O ",
                # dummy separator
                " .   O   x   O   .   O   .   O \n"
                " O   x   O   .   O   x   O   . \n"
                " .   x   O   O   .   .   O   O \n"
                " O   O   .   .   O   O   .   . \n"
                " .   x   x   x   .   x   .   x \n"
                " x   O   x   O   O   x   O   O ",
            ),
        )
        sample_grid_vectors = (
            (FieldTypeGrid(grid), FieldTypeGrid(grid))
            for grid in self.sample_fieldtypegrids
        )
        for sample_grid_vector, expected_grid_repr_vector in zip(
            sample_grid_vectors, expected_grid_repr_vectors
        ):
            for sample_grid, params, expected_grid_repr in zip(
                sample_grid_vector, params_vector, expected_grid_repr_vector
            ):
                with self.subTest():
                    sample_grid.replace_fields_in_series(*params)
                    self.assertEqual(
                        parse_fieldtypegrid(expected_grid_repr), sample_grid
                    )
