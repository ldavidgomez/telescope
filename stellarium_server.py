import argparse
import json
import socket
import socketserver
import struct
import threading
import time
from pathlib import Path

from astronomy import horizontal_to_j2000, j2000_to_horizontal
from imu import TelescopeImu


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 10001
DEFAULT_INTERVAL_SECONDS = 0.5
DEFAULT_CONFIG_FILE = Path(__file__).with_name("telescope_config.json")
DEFAULT_LCD = "/dev/ttyACM0"

# Vega (J2000) provides an easy object to search for during the connection test.
DEFAULT_RA_DEGREES = 279.23473479
DEFAULT_DEC_DEGREES = 38.78368896

POSITION_MESSAGE = 0
POSITION_MESSAGE_LENGTH = 24
GOTO_MESSAGE_LENGTH = 20
FULL_CIRCLE = 1 << 32
QUARTER_CIRCLE = 1 << 30


def encode_ra(ra_degrees):
    return round((ra_degrees % 360.0) / 360.0 * FULL_CIRCLE) % FULL_CIRCLE


def encode_dec(dec_degrees):
    dec_degrees = max(-90.0, min(90.0, dec_degrees))
    return round(dec_degrees / 90.0 * QUARTER_CIRCLE)


def decode_ra(encoded_ra):
    return encoded_ra / FULL_CIRCLE * 360.0


def decode_dec(encoded_dec):
    return encoded_dec / QUARTER_CIRCLE * 90.0


def current_position_message(ra_degrees, dec_degrees, timestamp_us=None):
    if timestamp_us is None:
        timestamp_us = time.time_ns() // 1_000

    return struct.pack(
        "<HHQIii",
        POSITION_MESSAGE_LENGTH,
        POSITION_MESSAGE,
        timestamp_us,
        encode_ra(ra_degrees),
        encode_dec(dec_degrees),
        0,
    )


def decode_goto_message(message):
    if len(message) != GOTO_MESSAGE_LENGTH:
        return None

    length, message_type, _, encoded_ra, encoded_dec = struct.unpack(
        "<HHQIi", message
    )
    if length != GOTO_MESSAGE_LENGTH or message_type != POSITION_MESSAGE:
        return None

    return decode_ra(encoded_ra), decode_dec(encoded_dec)


def load_config(config_file):
    config = json.loads(Path(config_file).read_text(encoding="utf-8"))
    observer = config["observer"]
    latitude = float(observer["latitude_deg"])
    longitude = float(observer["longitude_deg"])

    if not -90.0 <= latitude <= 90.0:
        raise ValueError("Observer latitude must be between -90 and +90 degrees.")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(
            "Observer longitude must be between -180 and +180 degrees."
        )
    return config, (latitude, longitude)


def shortest_angle(target_degrees, current_degrees):
    return (target_degrees - current_degrees + 180.0) % 360.0 - 180.0


class LcdDisplay:
    def __init__(self, device):
        self.stream = None
        if device:
            try:
                self.stream = open(device, "wb", buffering=0)
                time.sleep(2)
            except OSError as error:
                print(f"LCD unavailable: {error}", flush=True)

    def show(self, line1, line2):
        if self.stream is None:
            return
        self.stream.write(b"\xFE\x47\x01\x01")
        self.stream.write(line1[:16].ljust(16).encode("ascii"))
        self.stream.write(b"\xFE\x47\x01\x02")
        self.stream.write(line2[:16].ljust(16).encode("ascii"))

    def close(self):
        if self.stream is not None:
            self.stream.close()


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

    def log(self, message):
        with self.print_lock:
            print(message, flush=True)

    def set_target(self, ra_degrees, dec_degrees):
        with self.target_lock:
            self.target = (ra_degrees, dec_degrees)
            self.last_display_update = 0.0
        self.update_display(force=True)

    def read_current_position(self):
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
            f"dA{delta_azimuth:+05.1f} dH{delta_altitude:+05.1f}",
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
                ra_degrees, dec_degrees = self.server.read_current_position()
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
    parser.add_argument("--lcd", default=DEFAULT_LCD)
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
    args = parse_arguments()
    if not -90.0 <= args.dec_deg <= 90.0:
        raise SystemExit("Declination must be between -90 and +90 degrees.")
    if args.interval <= 0:
        raise SystemExit("The update interval must be greater than zero.")

    config, observer = load_config(args.config)
    display = LcdDisplay(args.lcd)
    display.show("Stellarium", "Starting IMU")

    position_provider = None
    if not args.fixed_position:
        imu_settings = config["imu"]
        calibration_file = Path(args.config).parent / imu_settings.get(
            "calibration_file", "compass_calibration.json"
        )
        position_provider = TelescopeImu(calibration_file, imu_settings)

    try:
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
            print(
                f"Stellarium telescope server listening on port {args.port}.\n"
                f"Position source: {position_mode}.\n"
                f"Observer: {observer[0]:+.4f} deg, {observer[1]:+.4f} deg.\n"
                "Press Ctrl+C to stop.",
                flush=True,
            )
            try:
                server.serve_forever(poll_interval=0.2)
            except KeyboardInterrupt:
                print("\nServer stopped.")
    finally:
        display.close()


if __name__ == "__main__":
    main()
