import argparse
import logging
import socket
import socketserver
import struct
import threading
import time
from pathlib import Path

from astronomy import horizontal_to_j2000, j2000_to_horizontal
from configuration import load_config
from display import DEFAULT_LCD_DEVICE, LcdDisplay
from imu import TelescopeImu
from stellarium_protocol import (
    current_position_message,
    decode_goto_message,
)


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 10001
DEFAULT_INTERVAL_SECONDS = 0.5
DEFAULT_GUIDANCE_TOLERANCE_DEGREES = 0.5
DEFAULT_CONFIG_FILE = Path(__file__).with_name("telescope_config.json")
LOGGER = logging.getLogger(__name__)

# Vega (J2000) provides an easy object to search for during the connection test.
DEFAULT_RA_DEGREES = 279.23473479
DEFAULT_DEC_DEGREES = 38.78368896

def shortest_angle(target_degrees, current_degrees):
    return (target_degrees - current_degrees + 180.0) % 360.0 - 180.0


def format_guidance_axis(
    label,
    difference_degrees,
    positive_symbol,
    negative_symbol,
    tolerance_degrees=DEFAULT_GUIDANCE_TOLERANCE_DEGREES,
):
    if abs(difference_degrees) <= tolerance_degrees:
        return f"{label} OK"
    symbol = positive_symbol if difference_degrees > 0 else negative_symbol
    magnitude = abs(difference_degrees)
    formatted = f"{magnitude:.1f}" if magnitude < 100.0 else f"{magnitude:.0f}"
    return f"{label}{symbol}{formatted}"


def format_guidance_line(delta_azimuth, delta_altitude):
    azimuth = format_guidance_axis("AZ", delta_azimuth, ">", "<")
    altitude = format_guidance_axis("AL", delta_altitude, "^", "v")
    return f"{azimuth} {altitude}"


class TelescopeServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        address,
        handler,
        ra_degrees,
        dec_degrees,
        interval,
        observer,
        display,
        position_provider=None,
    ):
        super().__init__(address, handler)
        self.ra_degrees = ra_degrees
        self.dec_degrees = dec_degrees
        self.interval = interval
        self.observer = observer
        self.display = display
        self.position_provider = position_provider
        self.target = None
        self.current_horizontal = None
        self.last_display_update = 0.0
        self.print_lock = threading.Lock()
        self.target_lock = threading.Lock()
        self.position_lock = threading.Lock()
        self.fatal_error = None

    def log(self, message):
        with self.print_lock:
            LOGGER.info(message)

    def report_hardware_failure(self, error):
        with self.print_lock:
            if self.fatal_error is not None:
                return
            self.fatal_error = error
            LOGGER.error("IMU read failed; stopping the server: %s", error)
        # BaseServer.shutdown() must run outside the serve_forever thread.
        threading.Thread(target=self.shutdown, daemon=True).start()

    def set_target(self, ra_degrees, dec_degrees):
        with self.target_lock:
            self.target = (ra_degrees, dec_degrees)
            self.last_display_update = 0.0
        self.update_display(force=True)

    def read_current_position(self):
        with self.position_lock:
            if self.position_provider is None:
                azimuth, altitude = j2000_to_horizontal(
                    self.ra_degrees,
                    self.dec_degrees,
                    *self.observer,
                )
                self.current_horizontal = (azimuth, altitude)
                return self.ra_degrees, self.dec_degrees

            azimuth, altitude, _ = self.position_provider.read_position()
            self.current_horizontal = (azimuth, altitude)
            return horizontal_to_j2000(
                azimuth,
                altitude,
                *self.observer,
            )

    def update_display(self, force=False):
        now = time.monotonic()
        with self.target_lock:
            if not force and now - self.last_display_update < 1.0:
                return
            target = self.target
            self.last_display_update = now

        if self.current_horizontal is None:
            return
        current_azimuth, current_altitude = self.current_horizontal
        current_line = f"AZ{current_azimuth:05.1f} AL{current_altitude:+05.1f}"

        if target is None:
            self.display.show(current_line, "Waiting target")
            return

        target_azimuth, target_altitude = j2000_to_horizontal(
            *target,
            *self.observer,
        )
        delta_azimuth = shortest_angle(target_azimuth, current_azimuth)
        delta_altitude = target_altitude - current_altitude
        self.display.show(
            current_line,
            format_guidance_line(delta_azimuth, delta_altitude),
        )
        return target_azimuth, target_altitude


class TelescopeRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.buffer = bytearray()
        self.server.log(f"Stellarium connected from {self.client_address[0]}")

    def handle(self):
        next_send = 0.0

        while True:
            now = time.monotonic()
            if now >= next_send:
                try:
                    ra_degrees, dec_degrees = (
                        self.server.read_current_position()
                    )
                except (OSError, ValueError, KeyError) as error:
                    self.server.report_hardware_failure(error)
                    break
                message = current_position_message(
                    ra_degrees,
                    dec_degrees,
                )
                try:
                    self.request.sendall(message)
                except (BrokenPipeError, ConnectionResetError):
                    break
                self.server.update_display()
                next_send = now + self.server.interval

            timeout = max(0.01, min(0.1, next_send - time.monotonic()))
            self.request.settimeout(timeout)

            try:
                data = self.request.recv(1024)
            except socket.timeout:
                continue
            except ConnectionResetError:
                break

            if not data:
                break

            self.buffer.extend(data)
            self.process_messages()

    def process_messages(self):
        while len(self.buffer) >= 2:
            length = struct.unpack_from("<H", self.buffer)[0]
            if length < 4 or length > 1024:
                raise ValueError(f"Invalid Stellarium message length: {length}")
            if len(self.buffer) < length:
                return

            message = bytes(self.buffer[:length])
            del self.buffer[:length]

            target = decode_goto_message(message)
            if target is not None:
                ra_degrees, dec_degrees = target
                self.server.set_target(ra_degrees, dec_degrees)
                azimuth, altitude = j2000_to_horizontal(
                    ra_degrees,
                    dec_degrees,
                    *self.server.observer,
                )
                self.server.log(
                    "Requested target: "
                    f"RA {ra_degrees / 15.0:.4f} h, "
                    f"Dec {dec_degrees:+.4f} deg, "
                    f"Az {azimuth:.2f} deg, Alt {altitude:+.2f} deg"
                )

    def finish(self):
        self.server.log(f"Stellarium disconnected from {self.client_address[0]}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Expose the IMU telescope position to Stellarium."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--ra-deg", type=float, default=DEFAULT_RA_DEGREES)
    parser.add_argument("--dec-deg", type=float, default=DEFAULT_DEC_DEGREES)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_FILE))
    parser.add_argument("--lcd", default=DEFAULT_LCD_DEVICE)
    parser.add_argument(
        "--fixed-position",
        action="store_true",
        help="Use the fixed RA/Dec test position instead of the IMU.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL_SECONDS,
        help="Position update interval in seconds.",
    )
    return parser.parse_args()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_arguments()
    if not -90.0 <= args.dec_deg <= 90.0:
        raise SystemExit("Declination must be between -90 and +90 degrees.")
    if args.interval <= 0:
        raise SystemExit("The update interval must be greater than zero.")

    config = load_config(args.config)
    observer = config.observer.coordinates
    display = LcdDisplay(args.lcd)
    display.show("Stellarium", "Starting IMU")

    position_provider = None
    try:
        if not args.fixed_position:
            imu_settings = config.imu
            calibration_file = Path(args.config).parent / imu_settings.get(
                "calibration_file", "compass_calibration.json"
            )
            position_provider = TelescopeImu(calibration_file, imu_settings)
            # Fail at startup instead of accepting clients with a broken IMU.
            position_provider.read_position()

        with TelescopeServer(
            (args.host, args.port),
            TelescopeRequestHandler,
            args.ra_deg,
            args.dec_deg,
            args.interval,
            observer,
            display,
            position_provider,
        ) as server:
            position_mode = "fixed test position" if args.fixed_position else "IMU"
            LOGGER.info(
                "Stellarium telescope server listening on port %d.",
                args.port,
            )
            LOGGER.info("Position source: %s.", position_mode)
            if position_provider is not None and position_provider.fusion_enabled:
                LOGGER.info(
                    "Gyroscope fusion: enabled at %d Hz.",
                    position_provider.fusion_sample_rate,
                )
            LOGGER.info(
                "Observer: %+.4f deg, %+.4f deg.",
                observer[0],
                observer[1],
            )
            try:
                server.serve_forever(poll_interval=0.2)
            except KeyboardInterrupt:
                LOGGER.info("Server stopped.")
            if server.fatal_error is not None:
                raise RuntimeError("The IMU became unavailable") from server.fatal_error
    finally:
        if position_provider is not None:
            position_provider.close()
        display.close()


if __name__ == "__main__":
    main()
