import unittest

from imu import (
    Orientation,
    PositionSmoother,
    apply_calibration,
    calibration_from_extrema,
    calculate_orientation,
    map_telescope_position,
)


class ImuTest(unittest.TestCase):
    def test_calibration_from_extrema(self):
        calibration = calibration_from_extrema(
            {"x": -10, "y": -20, "z": -30},
            {"x": 10, "y": 20, "z": 30},
        )
        self.assertEqual(calibration["x_offset"], 0.0)
        self.assertEqual(calibration["y_offset"], 0.0)
        self.assertEqual(calibration["z_offset"], 0.0)
        self.assertAlmostEqual(calibration["x_scale"], 2.0)
        self.assertAlmostEqual(calibration["y_scale"], 1.0)
        self.assertAlmostEqual(calibration["z_scale"], 2.0 / 3.0)

    def test_apply_calibration(self):
        calibration = {
            "x_offset": 10.0,
            "y_offset": -10.0,
            "z_offset": 5.0,
            "x_scale": 2.0,
            "y_scale": 0.5,
            "z_scale": 1.0,
        }
        self.assertEqual(
            apply_calibration((15, 10, -5), calibration),
            (10.0, 10.0, -10.0),
        )

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
