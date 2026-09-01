import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from display import DEFAULT_LCD_DEVICE, LcdDisplay
from imu import (
    GYROSCOPE_SENSITIVITY_DPS,
    Lsm303Sensor,
    apply_calibration,
    calibrate_gyroscope_bias,
    calculate_orientation,
    load_calibration,
    remove_gyroscope_bias,
)


DEFAULT_DURATION_SECONDS = 30.0
DEFAULT_SAMPLE_RATE_HZ = 100
DEFAULT_GYROSCOPE_WARMUP_SECONDS = 1.0
DEFAULT_CALIBRATION_FILE = Path(__file__).with_name(
    "compass_calibration.json"
)
DEFAULT_OUTPUT_FILE = Path(__file__).with_name("imu_recording.csv")
DEFAULT_METADATA_FILE = Path(__file__).with_name("imu_recording.json")

CSV_FIELDS = [
    "unix_time_ns",
    "elapsed_s",
    "dt_s",
    "accel_raw_x",
    "accel_raw_y",
    "accel_raw_z",
    "mag_raw_x",
    "mag_raw_y",
    "mag_raw_z",
    "mag_corrected_x",
    "mag_corrected_y",
    "mag_corrected_z",
    "gyro_raw_x",
    "gyro_raw_y",
    "gyro_raw_z",
    "gyro_dps_x",
    "gyro_dps_y",
    "gyro_dps_z",
    "gyro_corrected_dps_x",
    "gyro_corrected_dps_y",
    "gyro_corrected_dps_z",
    "heading_2d_deg",
    "heading_tilt_deg",
    "roll_deg",
    "pitch_deg",
]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Record synchronized accelerometer, magnetometer, "
            "and gyroscope data."
        )
    )
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument(
        "--sample-rate",
        type=int,
        choices=(10, 50, 100),
        default=DEFAULT_SAMPLE_RATE_HZ,
    )
    parser.add_argument("--calibration", type=Path, default=DEFAULT_CALIBRATION_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_FILE)
    parser.add_argument("--gyro-bias-seconds", type=float, default=2.0)
    parser.add_argument(
        "--gyro-warmup-seconds",
        type=float,
        default=DEFAULT_GYROSCOPE_WARMUP_SECONDS,
    )
    parser.add_argument("--lcd", default=DEFAULT_LCD_DEVICE)
    parser.add_argument(
        "--no-lcd",
        action="store_true",
        help="Run without using the serial LCD.",
    )
    return parser.parse_args()


def recording_row(
    unix_time_ns,
    elapsed,
    delta_time,
    accelerometer,
    raw_magnetometer,
    corrected_magnetometer,
    raw_gyroscope,
    gyroscope_dps,
    corrected_gyroscope,
    orientation,
):
    return [
        unix_time_ns,
        f"{elapsed:.9f}",
        f"{delta_time:.9f}",
        *accelerometer,
        *raw_magnetometer,
        *(f"{value:.6f}" for value in corrected_magnetometer),
        *raw_gyroscope,
        *(f"{value:.6f}" for value in gyroscope_dps),
        *(f"{value:.6f}" for value in corrected_gyroscope),
        f"{orientation.heading_2d:.6f}",
        f"{orientation.heading:.6f}",
        f"{orientation.roll:.6f}",
        f"{orientation.pitch:.6f}",
    ]


def record_samples(sensor, display, writer, calibration, gyroscope_bias, args):
    period = 1.0 / args.sample_rate
    started = time.monotonic()
    previous_sample = None
    next_sample = started
    next_status = started
    sample_count = 0
    last_elapsed = 0.0
    completed = True

    try:
        while True:
            now = time.monotonic()
            if now < next_sample:
                time.sleep(next_sample - now)

            sampled_at = time.monotonic()
            elapsed = sampled_at - started
            if elapsed >= args.duration:
                break

            accelerometer = sensor.read_accelerometer()
            raw_magnetometer = sensor.read_magnetometer()
            corrected_magnetometer = apply_calibration(
                raw_magnetometer,
                calibration,
            )
            raw_gyroscope = sensor.read_gyroscope_raw()
            gyroscope_dps = tuple(
                value * GYROSCOPE_SENSITIVITY_DPS
                for value in raw_gyroscope
            )
            corrected_gyroscope = remove_gyroscope_bias(
                gyroscope_dps,
                gyroscope_bias,
            )
            orientation = calculate_orientation(
                *corrected_magnetometer,
                *accelerometer,
            )
            delta_time = (
                0.0
                if previous_sample is None
                else sampled_at - previous_sample
            )
            writer.writerow(
                recording_row(
                    time.time_ns(),
                    elapsed,
                    delta_time,
                    accelerometer,
                    raw_magnetometer,
                    corrected_magnetometer,
                    raw_gyroscope,
                    gyroscope_dps,
                    corrected_gyroscope,
                    orientation,
                )
            )

            sample_count += 1
            previous_sample = sampled_at
            last_elapsed = elapsed
            next_sample += period
            if next_sample <= sampled_at:
                next_sample = sampled_at + period

            if sampled_at >= next_status:
                remaining = max(0, round(args.duration - elapsed))
                display.show(
                    f"Recording {remaining:2d}s",
                    f"Samples {sample_count}",
                )
                print(
                    f"\r{elapsed:6.1f}s  samples: {sample_count:5d}  "
                    f"heading: {orientation.heading:6.1f}°",
                    end="",
                    flush=True,
                )
                next_status = sampled_at + 1.0
    except KeyboardInterrupt:
        completed = False
        print("\nRecording interrupted.")

    print()
    actual_rate = (
        (sample_count - 1) / last_elapsed
        if sample_count > 1 and last_elapsed > 0
        else 0.0
    )
    return sample_count, actual_rate, completed


def main():
    args = parse_arguments()
    if args.duration <= 0:
        raise SystemExit("Recording duration must be greater than zero.")
    if args.gyro_bias_seconds <= 0:
        raise SystemExit("Gyroscope bias duration must be greater than zero.")
    if args.gyro_warmup_seconds < 0:
        raise SystemExit("Gyroscope warm-up duration cannot be negative.")

    calibration = load_calibration(args.calibration)
    lcd_device = None if args.no_lcd else args.lcd
    bias_sample_count = max(
        1,
        round(args.gyro_bias_seconds * args.sample_rate),
    )
    metadata = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "requested_sample_rate_hz": args.sample_rate,
        "requested_duration_s": args.duration,
        "gyro_bias_duration_s": args.gyro_bias_seconds,
        "gyro_warmup_duration_s": args.gyro_warmup_seconds,
        "completed": False,
    }

    with (
        Lsm303Sensor(
            accelerometer_rate_hz=args.sample_rate,
            enable_gyroscope=True,
        ) as sensor,
        LcdDisplay(lcd_device) as display,
        args.output.open("w", newline="", encoding="utf-8") as output,
    ):
        writer = csv.writer(output)
        writer.writerow(CSV_FIELDS)
        display.show("Gyro warm-up", "Keep IMU still")
        print(
            f"Waiting {args.gyro_warmup_seconds:g} seconds for the "
            "gyroscope to stabilize."
        )
        time.sleep(args.gyro_warmup_seconds)
        display.show("Gyro calibration", "Keep IMU still")
        print(
            f"Keep the IMU still for {args.gyro_bias_seconds:g} seconds "
            "while the gyroscope bias is measured."
        )
        gyroscope_bias = calibrate_gyroscope_bias(
            sensor,
            sample_count=bias_sample_count,
            sample_interval_seconds=1.0 / args.sample_rate,
        )
        metadata["gyro_bias_dps"] = {
            axis: value for axis, value in zip("xyz", gyroscope_bias)
        }
        metadata["gyroscope_chip_id"] = (
            f"0x{sensor.gyroscope_chip_id:02x}"
        )
        print(
            "Gyroscope bias: "
            + ", ".join(
                f"{axis.upper()} {value:+.5f} dps"
                for axis, value in zip("xyz", gyroscope_bias)
            )
        )
        print(
            f"Recording {args.duration:g} seconds at "
            f"{args.sample_rate} Hz to {args.output}."
        )

        sample_count, actual_rate, completed = record_samples(
            sensor,
            display,
            writer,
            calibration,
            gyroscope_bias,
            args,
        )
        metadata["completed"] = completed
        if completed:
            display.show("Recording done", f"Samples {sample_count}")
        else:
            display.show("Recording", "Interrupted")

    metadata["sample_count"] = sample_count
    metadata["actual_sample_rate_hz"] = actual_rate
    metadata["finished_utc"] = datetime.now(timezone.utc).isoformat()
    args.metadata.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Metadata saved to {args.metadata}.")


if __name__ == "__main__":
    main()
