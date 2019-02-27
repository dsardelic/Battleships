import contextlib
import unittest.mock

from battleships.grid import Position, Series
from battleships.ship import Ship, ShipGrid
from test.unit.test_grid import parse_fieldtypegrid


class ShipGridTest(unittest.TestCase):
    def test_get_grid(self):
        sample_keys = [(3, Series.COLUMN), (2, Series.ROW), (1, Series.ROW)]
        sample_grid_reprs = [
            " .   .   . \n"  # dummy comment to counter Black formatting
            " .   O   . \n"
            " .   O   . \n"
            " .   O   . \n"
            " .   .   . ",
            " .   .   .   . \n"  # dummy comment to counter Black formatting
            " .   O   O   . \n"
            " .   .   .   . ",
            " .   .   . \n"  # dummy comment to counter Black formatting
            " .   O   . \n"
            " .   .   . ",
        ]
        for sample_key, sample_grid_repr in zip(sample_keys, sample_grid_reprs):
            with contextlib.suppress(KeyError):
                del ShipGrid._grids[sample_key]
            self.assertEqual(
                parse_fieldtypegrid(sample_grid_repr), ShipGrid.get_grid(*sample_key)
            )
            self.assertTrue(ShipGrid._grids[sample_key])
            # now cached
            self.assertEqual(
                parse_fieldtypegrid(sample_grid_repr), ShipGrid.get_grid(*sample_key)
            )


class ShipTest(unittest.TestCase):
    def setUp(self):
        self.sample_ships = (
            Ship(Position(2, 7), 3, Series.ROW),
            Ship(Position(1, 1), 1, Series.ROW),
            Ship(Position(7, 10), 4, Series.COLUMN),
            Ship(Position(3, 3), 2, Series.COLUMN),
        )

    @unittest.mock.patch.object(ShipGrid, "get_grid")
    def test_grid(self, mocked_shipgrid_grids):
        expected_params_vector = (
            (ship.size, ship.orientation) for ship in self.sample_ships
        )
        for sample_ship, expected_params in zip(
            self.sample_ships, expected_params_vector
        ):
            with self.subTest():
                sample_ship.grid
                mocked_shipgrid_grids.assert_called_once_with(*expected_params)
                mocked_shipgrid_grids.reset_mock()

    def test_ship_fields_count_in_series(self):
        expected_values = (
            {Series.ROW: 3, Series.COLUMN: 1},
            {Series.ROW: 1, Series.COLUMN: 1},
            {Series.ROW: 1, Series.COLUMN: 4},
            {Series.ROW: 1, Series.COLUMN: 2},
        )
        for ship, expected_value in zip(self.sample_ships, expected_values):
            ship._ship_fields_count_in_series = {}
            with self.subTest():
                self.assertEqual(expected_value, ship.ship_fields_count_in_series)
                self.assertNotEqual(ship._ship_fields_count_in_series, {})
                # now cached
                self.assertEqual(expected_value, ship.ship_fields_count_in_series)

    def test_max_ship_field_index_in_series(self):
        expected_values = (
            {Series.ROW: 2, Series.COLUMN: 9},
            {Series.ROW: 1, Series.COLUMN: 1},
            {Series.ROW: 10, Series.COLUMN: 10},
            {Series.ROW: 4, Series.COLUMN: 3},
        )
        for ship, expected_value in zip(self.sample_ships, expected_values):
            ship._max_ship_field_index_in_series = {}
            with self.subTest():
                self.assertEqual(expected_value, ship.max_ship_field_index_in_series)
                self.assertNotEqual(ship._max_ship_field_index_in_series, {})
                # now cached
                self.assertEqual(expected_value, ship.max_ship_field_index_in_series)

    def test_create_reach_object(self):
        params_vector = ((range, False), (range, True), (slice, False), (slice, True))
        expected_results_vector = (
            (
                {Series.ROW: range(2, 3), Series.COLUMN: range(7, 10)},
                {Series.ROW: range(1, 4), Series.COLUMN: range(6, 11)},
                {Series.ROW: slice(2, 3), Series.COLUMN: slice(7, 10)},
                {Series.ROW: slice(1, 4), Series.COLUMN: slice(6, 11)},
            ),
            (
                {Series.ROW: range(1, 2), Series.COLUMN: range(1, 2)},
                {Series.ROW: range(0, 3), Series.COLUMN: range(0, 3)},
                {Series.ROW: slice(1, 2), Series.COLUMN: slice(1, 2)},
                {Series.ROW: slice(0, 3), Series.COLUMN: slice(0, 3)},
            ),
            (
                {Series.ROW: range(7, 11), Series.COLUMN: range(10, 11)},
                {Series.ROW: range(6, 12), Series.COLUMN: range(9, 12)},
                {Series.ROW: slice(7, 11), Series.COLUMN: slice(10, 11)},
                {Series.ROW: slice(6, 12), Series.COLUMN: slice(9, 12)},
            ),
            (
                {Series.ROW: range(3, 5), Series.COLUMN: range(3, 4)},
                {Series.ROW: range(2, 6), Series.COLUMN: range(2, 5)},
                {Series.ROW: slice(3, 5), Series.COLUMN: slice(3, 4)},
                {Series.ROW: slice(2, 6), Series.COLUMN: slice(2, 5)},
            ),
        )
        for sample_ship, expected_results in zip(
            self.sample_ships, expected_results_vector
        ):
            for params, expected_result in zip(params_vector, expected_results):
                with self.subTest():
                    self.assertEqual(
                        expected_result, sample_ship._create_reach_object(*params)
                    )

    @unittest.mock.patch.object(Ship, "_create_reach_object")
    def test_ship_fields_range(self, mock_create_reach_object):
        for sample_ship in self.sample_ships:
            sample_ship._ship_fields_range = {}
            with self.subTest():
                sample_ship.ship_fields_range
                self.assertNotEqual(sample_ship._ship_fields_range, {})
                mock_create_reach_object.assert_called_once_with(range, False)
                mock_create_reach_object.reset_mock()
                # now cached
                sample_ship.ship_fields_range
                mock_create_reach_object.assert_not_called()

    @unittest.mock.patch.object(Ship, "_create_reach_object")
    def test_ship_fields_slice(self, mock_create_reach_object):
        for sample_ship in self.sample_ships:
            sample_ship._ship_fields_slice = {}
            with self.subTest():
                sample_ship.ship_fields_slice
                self.assertNotEqual(sample_ship._ship_fields_slice, {})
                mock_create_reach_object.assert_called_once_with(slice, False)
                mock_create_reach_object.reset_mock()
                # now cached
                sample_ship.ship_fields_slice
                mock_create_reach_object.assert_not_called()

    @unittest.mock.patch.object(Ship, "_create_reach_object")
    def test_zoc_slice(self, mock_create_reach_object):
        for sample_ship in self.sample_ships:
            sample_ship._zoc_slice = {}
            with self.subTest():
                sample_ship.zoc_slice
                self.assertNotEqual(sample_ship._zoc_slice, {})
                mock_create_reach_object.assert_called_once_with(slice, True)
                mock_create_reach_object.reset_mock()
                # now cached
                sample_ship.zoc_slice
                mock_create_reach_object.assert_not_called()
