import unittest

from telescope.configuration import config_from_dict


class ConfigurationTest(unittest.TestCase):
    def test_loads_and_converts_configuration_values(self):
        config = config_from_dict(
            {
                "observer": {
                    "latitude_deg": "36.4753",
                    "longitude_deg": "-6.1946",
                    "altitude_m": "8",
                },
                "imu": {
                    "altitude_source": "pitch",
                    "deadband_deg": "0.3",
                },
            }
        )
        self.assertEqual(config.observer.coordinates, (36.4753, -6.1946))
        self.assertEqual(config.observer.altitude_m, 8.0)
        self.assertEqual(config.imu["deadband_deg"], 0.3)
        self.assertEqual(config.display["mode"], "auto")
        self.assertEqual(config.display["night_rgb"], (255, 0, 0))

    def test_rejects_invalid_observer_latitude(self):
        with self.assertRaises(ValueError):
            config_from_dict(
                {
                    "observer": {
                        "latitude_deg": 91,
                        "longitude_deg": 0,
                    },
                    "imu": {},
                }
            )

    def test_validates_fusion_configuration(self):
        data = {
            "observer": {"latitude_deg": 0, "longitude_deg": 0},
            "imu": {
                "fusion_enabled": True,
                "fusion_sample_rate_hz": "100",
                "fusion_time_constant_s": "0.1",
                "gyroscope_bias_dps": [1, 2, 3],
                "gyroscope_signs": [1, -1, -1],
            },
        }

        config = config_from_dict(data)

        self.assertEqual(config.imu["fusion_sample_rate_hz"], 100.0)
        self.assertEqual(config.imu["gyroscope_bias_dps"], (1.0, 2.0, 3.0))

    def test_requires_bias_when_fusion_is_enabled(self):
        with self.assertRaisesRegex(ValueError, "gyroscope_bias_dps"):
            config_from_dict(
                {
                    "observer": {"latitude_deg": 0, "longitude_deg": 0},
                    "imu": {"fusion_enabled": True},
                }
            )

    def test_loads_display_settings(self):
        config = config_from_dict(
            {
                "observer": {"latitude_deg": 0, "longitude_deg": 0},
                "imu": {},
                "display": {
                    "mode": "night",
                    "night_rgb": [120, 0, 0],
                    "night_brightness": "40",
                },
            }
        )

        self.assertEqual(config.display["mode"], "night")
        self.assertEqual(config.display["night_rgb"], (120, 0, 0))
        self.assertEqual(config.display["night_brightness"], 40)

    def test_rejects_overlapping_twilight_thresholds(self):
        with self.assertRaisesRegex(ValueError, "lower than day"):
            config_from_dict(
                {
                    "observer": {"latitude_deg": 0, "longitude_deg": 0},
                    "imu": {},
                    "display": {
                        "night_sun_altitude_deg": -4,
                        "day_sun_altitude_deg": -6,
                    },
                }
            )


if __name__ == "__main__":
    unittest.main()
