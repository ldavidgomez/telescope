import unittest

from configuration import config_from_dict


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


if __name__ == "__main__":
    unittest.main()
