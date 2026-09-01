import struct
import unittest

from stellarium_protocol import (
    POSITION_MESSAGE_LENGTH,
    current_position_message,
    decode_dec,
    decode_goto_message,
    decode_ra,
    encode_dec,
    encode_ra,
)
from stellarium_server import format_guidance_line, shortest_angle


class StellariumProtocolTest(unittest.TestCase):
    def test_shortest_angle(self):
        self.assertAlmostEqual(shortest_angle(10.0, 350.0), 20.0)
        self.assertAlmostEqual(shortest_angle(350.0, 10.0), -20.0)

    def test_formats_directional_guidance(self):
        self.assertEqual(
            format_guidance_line(85.2, 12.4),
            "AZ>85.2 AL^12.4",
        )
        self.assertEqual(
            format_guidance_line(-20.0, -4.5),
            "AZ<20.0 ALv4.5",
        )

    def test_guidance_uses_ok_inside_tolerance(self):
        self.assertEqual(
            format_guidance_line(0.5, -0.49),
            "AZ OK AL OK",
        )

    def test_guidance_keeps_shortest_azimuth_direction(self):
        delta = shortest_angle(10.0, 350.0)
        self.assertEqual(format_guidance_line(delta, 0.0), "AZ>20.0 AL OK")

    def test_angle_encoding_round_trip(self):
        for ra_degrees in (0.0, 90.0, 180.0, 279.23473479, 359.999):
            self.assertAlmostEqual(
                decode_ra(encode_ra(ra_degrees)), ra_degrees, places=6
            )

        for dec_degrees in (-90.0, -45.0, 0.0, 38.78368896, 90.0):
            self.assertAlmostEqual(
                decode_dec(encode_dec(dec_degrees)), dec_degrees, places=6
            )

    def test_current_position_packet(self):
        message = current_position_message(180.0, -45.0, timestamp_us=123)
        self.assertEqual(len(message), POSITION_MESSAGE_LENGTH)

        length, message_type, timestamp, ra, dec, status = struct.unpack(
            "<HHQIii", message
        )
        self.assertEqual(length, 24)
        self.assertEqual(message_type, 0)
        self.assertEqual(timestamp, 123)
        self.assertEqual(ra, 0x80000000)
        self.assertEqual(dec, -0x20000000)
        self.assertEqual(status, 0)

    def test_goto_packet(self):
        message = struct.pack(
            "<HHQIi",
            20,
            0,
            456,
            encode_ra(120.0),
            encode_dec(35.0),
        )
        ra_degrees, dec_degrees = decode_goto_message(message)
        self.assertAlmostEqual(ra_degrees, 120.0, places=6)
        self.assertAlmostEqual(dec_degrees, 35.0, places=6)


if __name__ == "__main__":
    unittest.main()
