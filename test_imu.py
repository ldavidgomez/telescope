import unittest

from imu import (
    ComplementaryOrientationFilter,
    GYROSCOPE,
    GYROSCOPE_SENSITIVITY_DPS,
    Lsm303Sensor,
    Orientation,
    PositionSmoother,
    apply_calibration,
    calibrate_gyroscope_bias,
    calibration_from_extrema,
    calculate_orientation,
    map_telescope_position,
    remove_gyroscope_bias,
)


class FakeBus:
    def __init__(self):
        self.writes = []

    def read_byte_data(self, address, register):
        self.asserted_read = (address, register)
        return 0xD7

    def write_byte_data(self, address, register, value):
        self.writes.append((address, register, value))

    def read_i2c_block_data(self, address, register, length):
        if address != GYROSCOPE:
            raise AssertionError(f"Unexpected address: {address:#x}")
        return [0xE8, 0x03, 0x18, 0xFC, 0xFF, 0x7F]


class FakeGyroscope:
    def __init__(self, values):
        self.values = iter(values)

    def read_gyroscope(self):
        return next(self.values)


class ImuTest(unittest.TestCase):
    def test_complementary_filter_uses_gyro_and_wraps_heading(self):
        orientation_filter = ComplementaryOrientationFilter(
            time_constant_seconds=1.0,
        )
        initial = Orientation(359.0, 359.0, 0.0, 0.0)
        orientation_filter.update(initial, (0.0, 0.0, 0.0), 0.0)

        result = orientation_filter.update(
            Orientation(1.0, 1.0, 0.0, 0.0),
            (10.0, -20.0, -5.0),
            0.1,
        )

        self.assertGreater(result.heading, 359.0)
        self.assertLess(result.heading, 360.0)
        self.assertGreater(result.roll, 0.0)
        self.assertGreater(result.pitch, 0.0)

    def test_complementary_filter_can_follow_measurements_exactly(self):
        orientation_filter = ComplementaryOrientationFilter(
            time_constant_seconds=0.0,
        )
        orientation_filter.update(
            Orientation(10.0, 10.0, 1.0, 2.0),
            (0.0, 0.0, 0.0),
            0.0,
        )
        measured = Orientation(20.0, 20.0, 3.0, 4.0)

        self.assertEqual(
            orientation_filter.update(
                measured,
                (100.0, 100.0, 100.0),
                1.0,
            ),
            measured,
        )

    def test_reads_l3gd20h_gyroscope_in_degrees_per_second(self):
        bus = FakeBus()
        sensor = Lsm303Sensor(bus=bus, enable_gyroscope=True)

        self.assertEqual(sensor.read_gyroscope_raw(), (1000, -1000, 32767))
        self.assertEqual(bus.asserted_read, (GYROSCOPE, 0x0F))
        self.assertIn((GYROSCOPE, 0x20, 0x0F), bus.writes)
        self.assertIn((GYROSCOPE, 0x23, 0x80), bus.writes)

        values = sensor.read_gyroscope()
        self.assertAlmostEqual(values[0], 1000 * GYROSCOPE_SENSITIVITY_DPS)
        self.assertAlmostEqual(values[1], -1000 * GYROSCOPE_SENSITIVITY_DPS)

    def test_calibrates_and_removes_gyroscope_bias(self):
        sensor = FakeGyroscope(
            [
                (1.0, -2.0, 0.25),
                (3.0, -4.0, 0.75),
            ]
        )
        bias = calibrate_gyroscope_bias(
            sensor,
            sample_count=2,
            sample_interval_seconds=0.0,
            sleep=lambda seconds: None,
        )
        self.assertEqual(bias, (2.0, -3.0, 0.5))
        self.assertEqual(
            remove_gyroscope_bias((3.0, -1.0, 1.0), bias),
            (1.0, 2.0, 0.5),
        )

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
