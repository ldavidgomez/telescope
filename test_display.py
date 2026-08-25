import unittest

from display import LcdDisplay


class FakeStream:
    def __init__(self):
        self.data = bytearray()
        self.closed = False

    def write(self, data):
        self.data.extend(data)

    def close(self):
        self.closed = True


class DisplayTest(unittest.TestCase):
    def test_formats_two_sixteen_character_lines(self):
        stream = FakeStream()
        display = LcdDisplay(
            "/dev/fake",
            opener=lambda *args, **kwargs: stream,
            sleep=lambda seconds: None,
        )

        self.assertTrue(display.show("12345678901234567", "Ready"))

        self.assertEqual(
            bytes(stream.data),
            b"\xFE\x47\x01\x01"
            b"1234567890123456"
            b"\xFE\x47\x01\x02"
            b"Ready           ",
        )
        display.close()
        self.assertTrue(stream.closed)

    def test_can_be_disabled(self):
        display = LcdDisplay(None)
        self.assertFalse(display.available)
        self.assertFalse(display.show("One", "Two"))


if __name__ == "__main__":
    unittest.main()
