import unittest

from engine import trends


class TrendTrafficTests(unittest.TestCase):
    def test_google_volume_bands_become_lower_bounds(self):
        self.assertEqual(trends._traffic_number("50K+"), 50_000)
        self.assertEqual(trends._traffic_number("1.2M+"), 1_200_000)
        self.assertEqual(trends._traffic_number("unknown"), 0)

    def test_demand_points_are_bounded_and_monotonic(self):
        samples = [0, 5_000, 20_000, 50_000, 100_000, 1_000_000]
        scores = [trends._demand_points(value) for value in samples]
        self.assertEqual(scores, sorted(scores))
        self.assertEqual(scores[-1], 35)


if __name__ == "__main__":
    unittest.main()
