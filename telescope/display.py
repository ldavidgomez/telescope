import logging
import time
from typing import Optional

from telescope.astronomy import sun_altitude


DEFAULT_LCD_DEVICE = "/dev/ttyACM0"
LCD_COMMAND = b"\xFE"
LCD_SET_BRIGHTNESS = b"\x99"
LCD_SET_RGB = b"\xD0"
LOGGER = logging.getLogger(__name__)


class LcdDisplay:
    """Small, fault-tolerant wrapper around the Adafruit serial LCD."""

    def __init__(
        self,
        device: Optional[str] = DEFAULT_LCD_DEVICE,
        reconnect_interval_seconds=5.0,
        opener=open,
        clock=time.monotonic,
        sleep=time.sleep,
    ):
        self.device = device
        self.reconnect_interval = reconnect_interval_seconds
        self._opener = opener
        self._clock = clock
        self._sleep = sleep
        self._stream = None
        self._last_connection_attempt = None
        self._connect()

    @property
    def available(self):
        return self._stream is not None

    def _connect(self):
        if not self.device or self._stream is not None:
            return self.available

        now = self._clock()
        if (
            self._last_connection_attempt is not None
            and now - self._last_connection_attempt < self.reconnect_interval
        ):
            return False

        self._last_connection_attempt = now
        try:
            self._stream = self._opener(self.device, "wb", buffering=0)
            # Opening the USB serial connection resets the LCD backpack.
            self._sleep(2)
            LOGGER.info("LCD connected at %s", self.device)
        except OSError as error:
            LOGGER.warning("LCD unavailable at %s: %s", self.device, error)
            self._stream = None
        return self.available

    def _disconnect(self, error=None):
        if error is not None:
            LOGGER.warning("LCD disconnected: %s", error)
        if self._stream is not None:
            try:
                self._stream.close()
            except OSError:
                pass
        self._stream = None

    def show(self, line1, line2):
        if not self._connect():
            return False

        try:
            self._stream.write(LCD_COMMAND + b"\x47\x01\x01")
            self._stream.write(line1[:16].ljust(16).encode("ascii"))
            self._stream.write(LCD_COMMAND + b"\x47\x01\x02")
            self._stream.write(line2[:16].ljust(16).encode("ascii"))
            return True
        except (OSError, UnicodeEncodeError) as error:
            self._disconnect(error)
            return False

    def clear(self):
        if not self._connect():
            return False
        try:
            self._stream.write(LCD_COMMAND + b"\x58")
            return True
        except OSError as error:
            self._disconnect(error)
            return False

    def set_backlight(self, rgb, brightness):
        values = tuple(int(value) for value in rgb)
        brightness = int(brightness)
        if len(values) != 3 or any(value < 0 or value > 255 for value in values):
            raise ValueError("RGB values must be between 0 and 255.")
        if not 0 <= brightness <= 255:
            raise ValueError("Brightness must be between 0 and 255.")
        if not self._connect():
            return False
        try:
            self._stream.write(
                LCD_COMMAND + LCD_SET_BRIGHTNESS + bytes([brightness])
            )
            self._stream.write(LCD_COMMAND + LCD_SET_RGB + bytes(values))
            return True
        except OSError as error:
            self._disconnect(error)
            return False

    def close(self):
        self._disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class SolarBacklightController:
    """Switch the LCD backlight using solar altitude and hysteresis."""

    def __init__(
        self,
        display,
        observer,
        settings,
        altitude_provider=sun_altitude,
    ):
        self.display = display
        self.observer = observer
        self.settings = settings
        self.altitude_provider = altitude_provider
        self.is_night = None
        self.applied_mode = None

    def set_observer(self, observer):
        self.observer = observer

    def _select_mode(self, moment):
        configured_mode = self.settings["mode"]
        if configured_mode != "auto":
            return configured_mode

        altitude = self.altitude_provider(*self.observer, moment)
        if self.is_night is None:
            self.is_night = (
                altitude <= self.settings["night_sun_altitude_deg"]
            )
        elif self.is_night:
            if altitude >= self.settings["day_sun_altitude_deg"]:
                self.is_night = False
        elif altitude <= self.settings["night_sun_altitude_deg"]:
            self.is_night = True
        return "night" if self.is_night else "day"

    def update(self, moment=None):
        mode = self._select_mode(moment)
        if mode == self.applied_mode:
            return mode

        if self.display.set_backlight(
            self.settings[f"{mode}_rgb"],
            self.settings[f"{mode}_brightness"],
        ):
            self.applied_mode = mode
            LOGGER.info("LCD backlight changed to %s mode.", mode)
        return mode
