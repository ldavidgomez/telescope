import argparse
import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path

from display import DEFAULT_LCD_DEVICE, LcdDisplay
from imu import Lsm303Sensor, calibration_from_extrema


DEFAULT_DURATION_SECONDS = 30.0
DEFAULT_CALIBRATION_FILE = Path(__file__).with_name(
    "compass_calibration.json"
)
DEFAULT_LOG_FILE = Path(__file__).with_name("compass_calibration.csv")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calibrate the telescope magnetometer."
    )
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_CALIBRATION_FILE)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG_FILE)
    parser.add_argument("--lcd", default=DEFAULT_LCD_DEVICE)
    parser.add_argument(
        "--no-lcd",
        action="store_true",
        help="Run without using the serial LCD.",
    )
    return parser.parse_args()


def collect_extrema(sensor, display, duration, writer):
    minimum = {axis: math.inf for axis in "xyz"}
    maximum = {axis: -math.inf for axis in "xyz"}
    started = time.monotonic()

    while True:
        elapsed = time.monotonic() - started
        if elapsed >= duration:
            break

        values = sensor.read_magnetometer()
        # -4096 indicates an overflow reading from this magnetometer.
        if -4096 in values:
            continue

        writer.writerow(
            [
                datetime.now().isoformat(timespec="milliseconds"),
                f"{elapsed:.3f}",
                *values,
            ]
        )

        for axis, value in zip("xyz", values):
            minimum[axis] = min(minimum[axis], value)
            maximum[axis] = max(maximum[axis], value)

        remaining = max(0, math.ceil(duration - elapsed))
        display.show(f"Calibrate {remaining:2d}s", "Rotate all axes")
        print(
            f"\r{remaining:2d}s remaining  "
            f"X[{minimum['x']:5.0f},{maximum['x']:5.0f}]  "
            f"Y[{minimum['y']:5.0f},{maximum['y']:5.0f}]  "
            f"Z[{minimum['z']:5.0f},{maximum['z']:5.0f}]",
            end="",
            flush=True,
        )
        time.sleep(0.05)

    print()
    return minimum, maximum


def main():
    args = parse_arguments()
    if args.duration <= 0:
        raise SystemExit("Calibration duration must be greater than zero.")

    lcd_device = None if args.no_lcd else args.lcd
    print(f"Calibration log reset: {args.log}")
    print(f"Slowly rotate the IMU in every direction for {args.duration:g} seconds.")

    with (
        Lsm303Sensor() as sensor,
        LcdDisplay(lcd_device) as display,
        args.log.open("w", newline="", encoding="utf-8") as log,
    ):
        writer = csv.writer(log)
        writer.writerow(["timestamp", "elapsed_s", "raw_x", "raw_y", "raw_z"])

        try:
            minimum, maximum = collect_extrema(
                sensor,
                display,
                args.duration,
                writer,
            )
            calibration = calibration_from_extrema(minimum, maximum)
            args.output.write_text(
                json.dumps(calibration, indent=2) + "\n",
                encoding="utf-8",
            )
            display.show("Calibration OK", "Data saved")
            print(f"Calibration saved to {args.output}")
            print(json.dumps(calibration, indent=2))
        except KeyboardInterrupt:
            display.show("Telescope", "Cancelled")
            print("\nCalibration cancelled")


if __name__ == "__main__":
    main()
