import unittest
from datetime import datetime, timezone

from astronomy import horizontal_to_j2000, j2000_to_horizontal, julian_date


class AstronomyTest(unittest.TestCase):
    def test_j2000_epoch(self):
        moment = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
        self.assertAlmostEqual(julian_date(moment), 2451545.0, places=6)

    def test_vega_matches_stellarium_capture(self):
        moment = datetime(2026, 8, 24, 16, 1, 14, tzinfo=timezone.utc)
        azimuth, altitude = j2000_to_horizontal(
            279.23473479,
            38.78368896,
            36.4753,
            -6.1946,
            moment,
        )

        # Stellarium showed Az 63.90 deg and apparent Alt 34.22 deg.
        self.assertAlmostEqual(azimuth, 63.90, delta=0.05)
        self.assertAlmostEqual(altitude, 34.22, delta=0.05)

    def test_horizontal_round_trip(self):
        moment = datetime(2026, 8, 24, 16, 1, 14, tzinfo=timezone.utc)
        observer = (36.4753, -6.1946)
        expected = (279.23473479, 38.78368896)
        horizontal = j2000_to_horizontal(*expected, *observer, moment)
        actual = horizontal_to_j2000(*horizontal, *observer, moment)

        self.assertAlmostEqual(actual[0], expected[0], places=6)
        self.assertAlmostEqual(actual[1], expected[1], places=6)


if __name__ == "__main__":
    unittest.main()
