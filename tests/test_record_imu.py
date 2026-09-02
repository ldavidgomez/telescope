import unittest

from telescope.imu import Orientation
from tools.record_imu import CSV_FIELDS, recording_row


class ImuRecordingTest(unittest.TestCase):
    def test_recording_row_matches_csv_header(self):
        row = recording_row(
            123,
            0.5,
            0.01,
            (1, 2, 3),
            (4, 5, 6),
            (7.0, 8.0, 9.0),
            (10, 11, 12),
            (0.1, 0.2, 0.3),
            (0.01, 0.02, 0.03),
            Orientation(20.0, 21.0, 22.0, 23.0),
        )
        self.assertEqual(len(row), len(CSV_FIELDS))
        self.assertEqual(dict(zip(CSV_FIELDS, row))["gyro_raw_z"], 12)
        self.assertEqual(
            dict(zip(CSV_FIELDS, row))["heading_tilt_deg"],
            "21.000000",
        )


if __name__ == "__main__":
    unittest.main()
