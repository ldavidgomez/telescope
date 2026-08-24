import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path

from smbus import SMBus

SENSOR = 0x1E
LCD = "/dev/ttyACM0"
CALIBRATION_SECONDS = 30
CALIBRATION_FILE = Path(__file__).with_name("compass_calibration.json")
CALIBRATION_LOG_FILE = Path(__file__).with_name("compass_calibration.csv")

bus = SMBus(1)
bus.write_byte_data(SENSOR, 0x00, 0x14)  # 30 Hz
bus.write_byte_data(SENSOR, 0x01, 0x20)  # ±1.3 gauss
bus.write_byte_data(SENSOR, 0x02, 0x00)  # Continuous measurement mode

display = open(LCD, "wb", buffering=0)
time.sleep(2)


def signed_big_endian(high, low):
    value = (high << 8) | low
    return value - 65536 if value & 0x8000 else value


def read_magnetometer():
    # The sensor returns six consecutive bytes in X, Z, Y order.
    data = bus.read_i2c_block_data(SENSOR, 0x03, 6)
    return (
        signed_big_endian(data[0], data[1]),
        signed_big_endian(data[4], data[5]),
        signed_big_endian(data[2], data[3]),
    )


def show_lines(line1, line2):
    display.write(b"\xFE\x47\x01\x01")
    display.write(line1[:16].ljust(16).encode("ascii"))
    display.write(b"\xFE\x47\x01\x02")
    display.write(line2[:16].ljust(16).encode("ascii"))


minimum = {"x": math.inf, "y": math.inf, "z": math.inf}
maximum = {"x": -math.inf, "y": -math.inf, "z": -math.inf}
log = CALIBRATION_LOG_FILE.open("w", newline="", encoding="utf-8")
writer = csv.writer(log)
writer.writerow(["timestamp", "elapsed_s", "raw_x", "raw_y", "raw_z"])
log.flush()
started = time.monotonic()

print(f"Calibration log reset: {CALIBRATION_LOG_FILE}")
print("Slowly rotate the IMU in every direction for 30 seconds.")

try:
    while True:
        elapsed = time.monotonic() - started
        if elapsed >= CALIBRATION_SECONDS:
            break

        x, y, z = read_magnetometer()

        # -4096 indicates an overflow reading from this magnetometer.
        if -4096 in (x, y, z):
            continue

        writer.writerow(
            [
                datetime.now().isoformat(timespec="milliseconds"),
                f"{elapsed:.3f}",
                x,
                y,
                z,
            ]
        )
        log.flush()

        for axis, value in (("x", x), ("y", y), ("z", z)):
            minimum[axis] = min(minimum[axis], value)
            maximum[axis] = max(maximum[axis], value)

        remaining = math.ceil(CALIBRATION_SECONDS - elapsed)
        show_lines(f"Calibrate {remaining:2d}s", "Rotate all axes")
        print(
            f"\r{remaining:2d}s remaining  "
            f"X[{minimum['x']:5.0f},{maximum['x']:5.0f}]  "
            f"Y[{minimum['y']:5.0f},{maximum['y']:5.0f}]",
            end="",
            flush=True,
        )
        time.sleep(0.05)

    print()

    x_radius = (maximum["x"] - minimum["x"]) / 2.0
    y_radius = (maximum["y"] - minimum["y"]) / 2.0
    if x_radius <= 0 or y_radius <= 0:
        raise RuntimeError("Not enough movement to calibrate the X/Y axes")

    z_radius = (maximum["z"] - minimum["z"]) / 2.0
    if z_radius <= 0:
        raise RuntimeError("Not enough movement to calibrate the Z axis")

    average_radius = (x_radius + y_radius + z_radius) / 3.0
    calibration = {
        "x_offset": (maximum["x"] + minimum["x"]) / 2.0,
        "y_offset": (maximum["y"] + minimum["y"]) / 2.0,
        "z_offset": (maximum["z"] + minimum["z"]) / 2.0,
        "x_scale": average_radius / x_radius,
        "y_scale": average_radius / y_radius,
        "z_scale": average_radius / z_radius,
        "minimum": minimum,
        "maximum": maximum,
    }

    CALIBRATION_FILE.write_text(
        json.dumps(calibration, indent=2) + "\n",
        encoding="utf-8",
    )

    show_lines("Calibration OK", "Data saved")
    print(f"Calibration saved to {CALIBRATION_FILE}")
    print(json.dumps(calibration, indent=2))

except KeyboardInterrupt:
    show_lines("Telescope", "Cancelled")
    print("\nCalibration cancelled")

finally:
    log.close()
    display.close()
