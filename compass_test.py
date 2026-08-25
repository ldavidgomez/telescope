import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from display import DEFAULT_LCD_DEVICE, LcdDisplay
from imu import (
    Lsm303Sensor,
    apply_calibration,
    calculate_orientation,
    load_calibration,
)


DEFAULT_CALIBRATION_FILE = Path(__file__).with_name(
    "compass_calibration.json"
)
DEFAULT_LOG_FILE = Path(__file__).with_name("compass_test.csv")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Read and log the calibrated telescope orientation."
    )
    parser.add_argument(
        "--calibration",
        type=Path,
        default=DEFAULT_CALIBRATION_FILE,
    )
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG_FILE)
    parser.add_argument("--lcd", default=DEFAULT_LCD_DEVICE)
    parser.add_argument(
        "--no-lcd",
        action="store_true",
        help="Run without using the serial LCD.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    calibration = load_calibration(args.calibration)
    lcd_device = None if args.no_lcd else args.lcd
    print(f"Calibration loaded from {args.calibration}")
    print(f"Log reset: {args.log}")

    with (
        Lsm303Sensor() as sensor,
        LcdDisplay(lcd_device) as display,
        args.log.open("w", newline="", encoding="utf-8") as log,
    ):
        writer = csv.writer(log)
        writer.writerow(
            [
                "timestamp",
                "elapsed_s",
                "heading_2d_deg",
                "heading_tilt_deg",
                "roll_deg",
                "pitch_deg",
                "accel_x",
                "accel_y",
                "accel_z",
                "raw_x",
                "raw_y",
                "raw_z",
                "corrected_x",
                "corrected_y",
                "corrected_z",
            ]
        )
        started = time.monotonic()

        try:
            while True:
                accelerometer = sensor.read_accelerometer()
                raw_magnetometer = sensor.read_magnetometer()
                corrected = apply_calibration(
                    raw_magnetometer,
                    calibration,
                )
                orientation = calculate_orientation(
                    *corrected,
                    *accelerometer,
                )

                writer.writerow(
                    [
                        datetime.now().isoformat(timespec="milliseconds"),
                        f"{time.monotonic() - started:.3f}",
                        f"{orientation.heading_2d:.3f}",
                        f"{orientation.heading:.3f}",
                        f"{orientation.roll:.3f}",
                        f"{orientation.pitch:.3f}",
                        *accelerometer,
                        *raw_magnetometer,
                        *(f"{value:.3f}" for value in corrected),
                    ]
                )
                log.flush()

                display.show(
                    f"Heading {orientation.heading:5.1f}",
                    f"R{orientation.roll:+5.1f} P{orientation.pitch:+5.1f}",
                )
                print(
                    f"\r2D heading: {orientation.heading_2d:6.1f}°  "
                    f"Tilt compensated: {orientation.heading:6.1f}°  "
                    f"Roll: {orientation.roll:6.1f}°  "
                    f"Pitch: {orientation.pitch:6.1f}°",
                    end="",
                    flush=True,
                )
                time.sleep(0.25)
        except KeyboardInterrupt:
            display.show("Telescope", "Test stopped")
            print()


if __name__ == "__main__":
    main()
