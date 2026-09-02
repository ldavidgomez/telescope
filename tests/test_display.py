import unittest
from unittest.mock import Mock, call

from telescope.display import LcdDisplay, SolarBacklightController


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

    def test_sets_backlight_brightness_and_rgb(self):
        stream = FakeStream()
        display = LcdDisplay(
            "/dev/fake",
            opener=lambda *args, **kwargs: stream,
            sleep=lambda seconds: None,
        )

        self.assertTrue(display.set_backlight((255, 0, 0), 80))

        self.assertEqual(bytes(stream.data), b"\xFE\x99\x50\xFE\xD0\xFF\x00\x00")

    def test_automatic_backlight_uses_twilight_hysteresis(self):
        display = Mock()
        display.set_backlight.return_value = True
        altitude_provider = Mock(side_effect=(-7.0, -5.0, -3.0))
        settings = {
            "mode": "auto",
            "night_sun_altitude_deg": -6.0,
            "day_sun_altitude_deg": -4.0,
            "day_rgb": (255, 255, 255),
            "day_brightness": 255,
            "night_rgb": (255, 0, 0),
            "night_brightness": 80,
        }
        controller = SolarBacklightController(
            display,
            (36.4753, -6.1946),
            settings,
            altitude_provider,
        )

        self.assertEqual(controller.update(), "night")
        self.assertEqual(controller.update(), "night")
        self.assertEqual(controller.update(), "day")

        self.assertEqual(
            display.set_backlight.call_args_list,
            [call((255, 0, 0), 80), call((255, 255, 255), 255)],
        )

    def test_manual_backlight_mode_skips_solar_calculation(self):
        display = Mock()
        display.set_backlight.return_value = True
        altitude_provider = Mock()
        settings = {
            "mode": "night",
            "night_sun_altitude_deg": -6.0,
            "day_sun_altitude_deg": -4.0,
            "day_rgb": (255, 255, 255),
            "day_brightness": 255,
            "night_rgb": (255, 0, 0),
            "night_brightness": 80,
        }
        controller = SolarBacklightController(
            display,
            (36.4753, -6.1946),
            settings,
            altitude_provider,
        )

        self.assertEqual(controller.update(), "night")

        altitude_provider.assert_not_called()
        display.set_backlight.assert_called_once_with((255, 0, 0), 80)


if __name__ == "__main__":
    unittest.main()
