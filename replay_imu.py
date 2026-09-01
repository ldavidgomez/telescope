import argparse
import csv
import math
from pathlib import Path

from imu import ComplementaryOrientationFilter, Orientation


DEFAULT_INPUT_FILE = Path(__file__).with_name("imu_recording.csv")
DEFAULT_OUTPUT_FILE = Path(__file__).with_name("imu_replay.csv")

OUTPUT_FIELDS = [
    "elapsed_s",
    "measured_heading_deg",
    "fused_heading_deg",
    "measured_roll_deg",
    "fused_roll_deg",
    "measured_pitch_deg",
    "fused_pitch_deg",
]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Replay recorded IMU data through the orientation filter."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--time-constant", type=float, default=0.1)
    return parser.parse_args()


def replay_rows(rows, time_constant_seconds):
    orientation_filter = ComplementaryOrientationFilter(
        time_constant_seconds=time_constant_seconds
    )
    for row in rows:
        measured = Orientation(
            heading_2d=float(row["heading_2d_deg"]),
            heading=float(row["heading_tilt_deg"]),
            roll=float(row["roll_deg"]),
            pitch=float(row["pitch_deg"]),
        )
        gyroscope = tuple(
            float(row[f"gyro_corrected_dps_{axis}"])
            for axis in "xyz"
        )
        fused = orientation_filter.update(
            measured,
            gyroscope,
            float(row["dt_s"]),
        )
        yield measured, fused, float(row["elapsed_s"])


def circular_error(first, second):
    return (first - second + 180.0) % 360.0 - 180.0


def main():
    args = parse_arguments()
    if args.time_constant < 0:
        raise SystemExit("Time constant cannot be negative.")

    squared_errors = {"heading": [], "roll": [], "pitch": []}
    with (
        args.input.open(newline="", encoding="utf-8") as input_file,
        args.output.open("w", newline="", encoding="utf-8") as output_file,
    ):
        reader = csv.DictReader(input_file)
        writer = csv.writer(output_file)
        writer.writerow(OUTPUT_FIELDS)
        sample_count = 0
        for measured, fused, elapsed in replay_rows(
            reader,
            args.time_constant,
        ):
            writer.writerow(
                [
                    f"{elapsed:.9f}",
                    f"{measured.heading:.6f}",
                    f"{fused.heading:.6f}",
                    f"{measured.roll:.6f}",
                    f"{fused.roll:.6f}",
                    f"{measured.pitch:.6f}",
                    f"{fused.pitch:.6f}",
                ]
            )
            squared_errors["heading"].append(
                circular_error(fused.heading, measured.heading) ** 2
            )
            squared_errors["roll"].append((fused.roll - measured.roll) ** 2)
            squared_errors["pitch"].append(
                (fused.pitch - measured.pitch) ** 2
            )
            sample_count += 1

    print(f"Replayed {sample_count} samples to {args.output}.")
    for name, errors in squared_errors.items():
        rms = math.sqrt(sum(errors) / len(errors)) if errors else 0.0
        print(f"{name.capitalize()} RMS correction: {rms:.2f} deg")


if __name__ == "__main__":
    main()
