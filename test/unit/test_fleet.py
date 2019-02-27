import copy
import unittest

from battleships.fleet import Fleet, InvalidShipSizeException


class FleetTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.sample_fleets = (
            Fleet({4: 1, 3: 2, 2: 3, 1: 4}),
            Fleet({5: 7, 2: 10, 1: 1}),
            Fleet({2: 1}),
            Fleet({}),
        )

    def test_distinct_ship_sizes(self):
        expected_results = ([4, 3, 2, 1], [5, 2, 1], [2], [])
        for fleet, expected_result in zip(self.sample_fleets, expected_results):
            with self.subTest():
                self.assertEqual(expected_result, fleet.distinct_ship_sizes)

    def test_longest_ship_size(self):
        expected_results = (4, 5, 2)
        for fleet, expected_result in zip(self.sample_fleets[:3], expected_results):
            with self.subTest():
                self.assertEqual(expected_result, fleet.longest_ship_size)
        with self.assertRaises(InvalidShipSizeException):
            self.sample_fleets[3].longest_ship_size

    def test_has_ships_remaining(self):
        expected_results = (True, True, True, False)
        for fleet, expected_result in zip(self.sample_fleets, expected_results):
            with self.subTest():
                self.assertEqual(expected_result, fleet.has_ships_remaining())

    def test_size_of_subfleet(self):
        expected_results = (4, 1, 0, 0)
        for fleet, expected_result in zip(self.sample_fleets, expected_results):
            with self.subTest():
                self.assertEqual(expected_result, fleet.size_of_subfleet(1))

    def test_add_ships_of_size(self):
        expected_results = (
            Fleet({4: 1, 3: 2, 2: 3, 1: 7}),
            Fleet({5: 7, 2: 10, 1: 4}),
            Fleet({2: 1, 1: 3}),
            Fleet({1: 3}),
        )
        for fleet, expected_result in zip(self.sample_fleets, expected_results):
            with self.subTest():
                fleet.add_ships_of_size(1, 3)
                self.assertEqual(expected_result, fleet)

    def test_remove_ship_of_size(self):
        expected_results = (Fleet({4: 1, 3: 2, 2: 3, 1: 3}), Fleet({5: 7, 2: 10}))
        for fleet, expected_result in zip(self.sample_fleets[:2], expected_results):
            with self.subTest():
                fleet.remove_ship_of_size(1)
                self.assertEqual(expected_result, fleet)
        for fleet in self.sample_fleets[2:]:
            with self.assertRaises(InvalidShipSizeException):
                fleet.remove_ship_of_size(1)

    def test_get_copy_of(self):
        for fleet in self.sample_fleets:
            with self.subTest():
                fleet_orig = copy.deepcopy(fleet)
                fleet_copy = Fleet.get_copy_of(fleet)
                self.assertFalse(fleet_copy is fleet)
                self.assertEqual(fleet_copy, fleet)
                self.assertEqual(fleet_copy, fleet_orig)
