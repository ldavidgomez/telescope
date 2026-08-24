import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path

from smbus import SMBus

ACCELEROMETER = 0x19
MAGNETOMETER = 0x1E
LCD = "/dev/ttyACM0"
CALIBRATION_FILE = Path(__file__).with_name("compass_calibration.json")
LOG_FILE = Path(__file__).with_name("compass_test.csv")

bus = SMBus(1)

# Accelerometer at 10 Hz with the X/Y/Z axes enabled
bus.write_byte_data(ACCELEROMETER, 0x20, 0x27)

# High-resolution mode, ±2 g range
bus.write_byte_data(ACCELEROMETER, 0x23, 0x88)

# Magnetometer at 30 Hz
bus.write_byte_data(MAGNETOMETER, 0x00, 0x14)

# ±1.3 gauss magnetic range
bus.write_byte_data(MAGNETOMETER, 0x01, 0x20)

# Continuous measurement mode
bus.write_byte_data(MAGNETOMETER, 0x02, 0x00)

display = open(LCD, "wb", buffering=0)
time.sleep(2)


def load_calibration():
    try:
        calibration = json.loads(CALIBRATION_FILE.read_text(encoding="utf-8"))
        if "z_offset" not in calibration and all(
            key in calibration for key in ("minimum", "maximum")
        ):
            minimum = calibration["minimum"]
            maximum = calibration["maximum"]
            x_radius = (maximum["x"] - minimum["x"]) / 2.0
            y_radius = (maximum["y"] - minimum["y"]) / 2.0
            z_radius = (maximum["z"] - minimum["z"]) / 2.0
            calibration["z_offset"] = (
                maximum["z"] + minimum["z"]
            ) / 2.0
            calibration["z_scale"] = (
                (x_radius + y_radius) / 2.0 / z_radius
                if z_radius > 0
                else 1.0
            )
        print(f"Calibration loaded from {CALIBRATION_FILE}")
        calibration.setdefault("z_offset", 0.0)
        calibration.setdefault("z_scale", 1.0)
        return calibration
    except FileNotFoundError:
        print("Warning: uncalibrated heading; run calibrate_compass.py")
        return {
            "x_offset": 0.0,
            "y_offset": 0.0,
            "z_offset": 0.0,
            "x_scale": 1.0,
            "y_scale": 1.0,
            "z_scale": 1.0,
        }


def signed_big_endian(high, low):
    value = (high << 8) | low
    return value - 65536 if value & 0x8000 else value


def signed_accelerometer_axis(data, position):
    value = (data[position + 1] << 8) | data[position]
    if value & 0x8000:
        value -= 65536
    return value >> 4


def read_accelerometer():
    data = bus.read_i2c_block_data(ACCELEROMETER, 0x28 | 0x80, 6)
    return (
        signed_accelerometer_axis(data, 0),
        signed_accelerometer_axis(data, 2),
        signed_accelerometer_axis(data, 4),
    )


def read_magnetometer():
    # The sensor returns six consecutive bytes in X, Z, Y order.
    data = bus.read_i2c_block_data(MAGNETOMETER, 0x03, 6)
    return (
        signed_big_endian(data[0], data[1]),
        signed_big_endian(data[4], data[5]),
        signed_big_endian(data[2], data[3]),
    )


def calculate_headings(mag_x, mag_y, mag_z, acc_x, acc_y, acc_z):
    heading_2d = math.degrees(math.atan2(mag_y, mag_x)) % 360.0

    # Tilt compensation for the sensor board's Z-up orientation. This follows
    # the geometry used by Adafruit's 10-DOF library for SENSOR_AXIS_Z.
    roll = math.atan2(
        acc_y,
        math.sqrt(acc_x * acc_x + acc_z * acc_z),
    )
    pitch = math.atan2(
        acc_x,
        math.sqrt(acc_y * acc_y + acc_z * acc_z),
    )

    cos_roll = math.cos(roll)
    sin_roll = math.sin(roll)
    cos_pitch = math.cos(-pitch)
    sin_pitch = math.sin(-pitch)

    horizontal_x = mag_x * cos_pitch + mag_z * sin_pitch
    horizontal_y = (
        mag_x * sin_roll * sin_pitch
        + mag_y * cos_roll
        - mag_z * sin_roll * cos_pitch
    )
    heading_tilt = math.degrees(
        math.atan2(horizontal_y, horizontal_x)
    ) % 360.0

    return (
        heading_2d,
        heading_tilt,
        math.degrees(roll),
        math.degrees(pitch),
    )


def show_lines(line1, line2):
    line1 = line1[:16].ljust(16)
    line2 = line2[:16].ljust(16)

    display.write(b"\xFE\x47\x01\x01")
    display.write(line1.encode("ascii"))

    display.write(b"\xFE\x47\x01\x02")
    display.write(line2.encode("ascii"))


calibration = load_calibration()
log = LOG_FILE.open("w", newline="", encoding="utf-8")
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
log.flush()
started = time.monotonic()
print(f"Log reset: {LOG_FILE}")

try:
    while True:
        accel_x, accel_y, accel_z = read_accelerometer()
        x, y, z = read_magnetometer()

        corrected_x = (
            (x - calibration["x_offset"]) * calibration["x_scale"]
        )
        corrected_y = (
            (y - calibration["y_offset"]) * calibration["y_scale"]
        )
        corrected_z = (
            (z - calibration["z_offset"]) * calibration["z_scale"]
        )

        heading_2d, heading_tilt, roll, pitch = calculate_headings(
            corrected_x,
            corrected_y,
            corrected_z,
            accel_x,
            accel_y,
            accel_z,
        )

        writer.writerow(
            [
                datetime.now().isoformat(timespec="milliseconds"),
                f"{time.monotonic() - started:.3f}",
                f"{heading_2d:.3f}",
                f"{heading_tilt:.3f}",
                f"{roll:.3f}",
                f"{pitch:.3f}",
                accel_x,
                accel_y,
                accel_z,
                x,
                y,
                z,
                f"{corrected_x:.3f}",
                f"{corrected_y:.3f}",
                f"{corrected_z:.3f}",
            ]
        )
        log.flush()

        show_lines(
            f"Heading {heading_tilt:5.1f}",
            f"R{roll:+5.1f} P{pitch:+5.1f}",
        )

        print(
            f"\r2D heading: {heading_2d:6.1f}°  "
            f"Tilt compensated: {heading_tilt:6.1f}°  "
            f"Roll: {roll:6.1f}°  Pitch: {pitch:6.1f}°",
            end="",
            flush=True,
        )

        time.sleep(0.25)

except KeyboardInterrupt:
    show_lines("Telescope", "Test stopped")
    print()

finally:
    log.close()
    display.close()
