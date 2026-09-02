import argparse
import logging
import socket
import socketserver
import struct
import threading
import time
from pathlib import Path

from telescope.astronomy import horizontal_to_j2000, j2000_to_horizontal
from telescope.configuration import load_config
from telescope.display import (
    DEFAULT_LCD_DEVICE,
    LcdDisplay,
    SolarBacklightController,
)
from telescope.imu import TelescopeImu
from telescope.lx200_protocol import Lx200Session
from telescope.stellarium_protocol import (
    current_position_message,
    decode_goto_message,
)


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 10001
DEFAULT_LX200_PORT = 10002
DEFAULT_INTERVAL_SECONDS = 0.5
DEFAULT_DISPLAY_INTERVAL_SECONDS = 0.5
DEFAULT_GUIDANCE_TOLERANCE_DEGREES = 0.5
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_FILE = PROJECT_ROOT / "telescope_config.json"
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
        display_interval=DEFAULT_DISPLAY_INTERVAL_SECONDS,
        backlight_controller=None,
    ):
        super().__init__(address, handler)
        self.ra_degrees = ra_degrees
        self.dec_degrees = dec_degrees
        self.interval = interval
        self.observer = observer
        self.display = display
        self.display_interval = display_interval
        self.position_provider = position_provider
        self.backlight_controller = backlight_controller
        self.target = None
        self.current_horizontal = None
        self.last_display_update = 0.0
        self.print_lock = threading.Lock()
        self.target_lock = threading.Lock()
        self.position_lock = threading.Lock()
        self.display_lock = threading.Lock()
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

    def set_observer(self, observer):
        self.observer = observer
        if self.backlight_controller is not None:
            self.backlight_controller.set_observer(observer)
        self.log(
            "Observer updated by LX200: "
            f"{observer[0]:+.4f} deg, {observer[1]:+.4f} deg"
        )
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

        with self.position_lock:
            current_horizontal = self.current_horizontal
        if current_horizontal is None:
            return
        current_azimuth, current_altitude = current_horizontal
        current_line = f"AZ{current_azimuth:05.1f} AL{current_altitude:+05.1f}"

        with self.display_lock:
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

    def refresh_display_until_stopped(self, stop_event):
        """Keep the LCD current even when no telescope client is polling."""
        while not stop_event.wait(self.display_interval):
            try:
                self.read_current_position()
            except (OSError, ValueError, KeyError) as error:
                self.report_hardware_failure(error)
                return
            if self.backlight_controller is not None:
                with self.display_lock:
                    self.backlight_controller.update()
            self.update_display(force=True)


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
                self.server.log(
                    "Ignoring a non-Stellarium probe from "
                    f"{self.client_address[0]}"
                )
                self.buffer.clear()
                return
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


class Lx200Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, telescope):
        super().__init__(address, Lx200RequestHandler)
        self.telescope = telescope


class Lx200RequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.buffer = ""
        telescope = self.server.telescope
        self.session = Lx200Session(
            telescope.read_current_position,
            self.set_target,
            telescope.observer,
            telescope.set_observer,
        )
        telescope.log(f"LX200 connected from {self.client_address[0]}")

    def handle(self):
        while True:
            try:
                data = self.request.recv(1024)
            except ConnectionResetError:
                break
            if not data:
                break

            alignment_queries = data.count(b"\x06")
            if alignment_queries:
                self.request.sendall(b"A" * alignment_queries)
                self.server.telescope.log(
                    "LX200 reported Alt-Az alignment mode."
                )
                data = data.replace(b"\x06", b"")
            if not data:
                continue
            self.buffer += data.decode("ascii", errors="ignore")
            self.process_commands()

    def process_commands(self):
        while "#" in self.buffer:
            raw_command, self.buffer = self.buffer.split("#", 1)
            colon = raw_command.find(":")
            if colon < 0:
                continue
            command = raw_command[colon + 1 :]
            try:
                response = self.session.execute(command)
            except (OSError, ValueError, KeyError) as error:
                self.server.telescope.report_hardware_failure(error)
                return
            if command in ("GR", "GD"):
                self.server.telescope.update_display()
            if command not in ("GR", "GD", "D", "GW"):
                self.server.telescope.log(
                    f"LX200 command {command!r}, response {response!r}"
                )
            if response:
                self.request.sendall(response.encode("ascii"))

    def set_target(self, ra_degrees, dec_degrees):
        telescope = self.server.telescope
        telescope.set_target(ra_degrees, dec_degrees)
        azimuth, altitude = j2000_to_horizontal(
            ra_degrees,
            dec_degrees,
            *telescope.observer,
        )
        telescope.log(
            "LX200 requested target: "
            f"RA {ra_degrees / 15.0:.4f} h, "
            f"Dec {dec_degrees:+.4f} deg, "
            f"Az {azimuth:.2f} deg, Alt {altitude:+.2f} deg"
        )

    def finish(self):
        self.server.telescope.log(
            f"LX200 disconnected from {self.client_address[0]}"
        )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Expose the IMU telescope position to Stellarium."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--lx200-port",
        type=int,
        default=DEFAULT_LX200_PORT,
        help="LX200 TCP port for Stellarium Mobile; use 0 to disable it.",
    )
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
    parser.add_argument(
        "--display-interval",
        type=float,
        default=DEFAULT_DISPLAY_INTERVAL_SECONDS,
        help="Autonomous LCD refresh interval in seconds.",
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
    if args.display_interval <= 0:
        raise SystemExit("The display interval must be greater than zero.")

    config = load_config(args.config)
    observer = config.observer.coordinates
    display = LcdDisplay(args.lcd)
    backlight_controller = SolarBacklightController(
        display,
        observer,
        config.display,
    )
    backlight_controller.update()
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
            args.display_interval,
            backlight_controller,
        ) as server:
            lx200_server = None
            lx200_thread = None
            if args.lx200_port:
                lx200_server = Lx200Server(
                    (args.host, args.lx200_port),
                    server,
                )
                lx200_thread = threading.Thread(
                    target=lx200_server.serve_forever,
                    kwargs={"poll_interval": 0.2},
                    daemon=True,
                )
                lx200_thread.start()
            display_stop = threading.Event()
            display_thread = threading.Thread(
                target=server.refresh_display_until_stopped,
                args=(display_stop,),
                daemon=True,
                name="lcd-refresh",
            )
            display_thread.start()
            position_mode = "fixed test position" if args.fixed_position else "IMU"
            LOGGER.info(
                "Stellarium telescope server listening on port %d.",
                args.port,
            )
            LOGGER.info("Position source: %s.", position_mode)
            if lx200_server is not None:
                LOGGER.info(
                    "LX200 telescope server listening on port %d.",
                    args.lx200_port,
                )
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
            finally:
                display_stop.set()
                display_thread.join(timeout=2.0)
                if lx200_server is not None:
                    lx200_server.shutdown()
                    lx200_server.server_close()
                    lx200_thread.join(timeout=2.0)
            if server.fatal_error is not None:
                raise RuntimeError("The IMU became unavailable") from server.fatal_error
    finally:
        if position_provider is not None:
            position_provider.close()
        display.close()


if __name__ == "__main__":
    main()
