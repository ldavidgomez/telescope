import unittest

from imu import (
    Orientation,
    PositionSmoother,
    calculate_orientation,
    map_telescope_position,
)


class ImuTest(unittest.TestCase):
    def test_position_smoothing_wraps_around_north(self):
        smoother = PositionSmoother(
            time_constant_seconds=1.0,
            deadband_degrees=0.0,
        )
        self.assertEqual(smoother.update(350.0, 0.0, now=0.0), (350.0, 0.0))

        azimuth, altitude = smoother.update(10.0, 10.0, now=1.0)
        self.assertAlmostEqual(azimuth, 2.6424, places=4)
        self.assertAlmostEqual(altitude, 6.3212, places=4)

    def test_position_smoothing_deadband(self):
        smoother = PositionSmoother(
            time_constant_seconds=0.0,
            deadband_degrees=0.3,
        )
        smoother.update(100.0, 20.0, now=0.0)
        self.assertEqual(
            smoother.update(100.2, 19.8, now=1.0),
            (100.0, 20.0),
        )

    def test_level_orientation(self):
        orientation = calculate_orientation(1.0, 0.0, 0.0, 0, 0, 1000)
        self.assertAlmostEqual(orientation.heading, 0.0)
        self.assertAlmostEqual(orientation.roll, 0.0)
        self.assertAlmostEqual(orientation.pitch, 0.0)

    def test_position_mapping(self):
        orientation = Orientation(0.0, 350.0, -4.0, 12.0)
        azimuth, altitude = map_telescope_position(
            orientation,
            {
                "altitude_source": "pitch",
                "altitude_sign": -1.0,
                "altitude_offset_deg": 5.0,
                "azimuth_offset_deg": 20.0,
            },
        )
        self.assertAlmostEqual(azimuth, 10.0)
        self.assertAlmostEqual(altitude, -7.0)


if __name__ == "__main__":
    unittest.main()
