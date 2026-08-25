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


if __name__ == "__main__":
    unittest.main()
