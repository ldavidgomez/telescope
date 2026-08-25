import logging
import time


DEFAULT_LCD_DEVICE = "/dev/ttyACM0"
LCD_COMMAND = b"\xFE"
LOGGER = logging.getLogger(__name__)


class LcdDisplay:
    """Small, fault-tolerant wrapper around the Adafruit serial LCD."""

    def __init__(
        self,
        device=DEFAULT_LCD_DEVICE,
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

    def close(self):
        self._disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
