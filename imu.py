import json
import math
import time
from dataclasses import dataclass
from pathlib import Path


ACCELEROMETER = 0x19
MAGNETOMETER = 0x1E
CALIBRATION_KEYS = tuple(
    f"{axis}_{suffix}"
    for axis in "xyz"
    for suffix in ("offset", "scale")
)


@dataclass(frozen=True)
class Orientation:
    heading_2d: float
    heading: float
    roll: float
    pitch: float


def signed_big_endian(high, low):
    value = (high << 8) | low
    return value - 65536 if value & 0x8000 else value


def signed_accelerometer_axis(data, position):
    value = (data[position + 1] << 8) | data[position]
    if value & 0x8000:
        value -= 65536
    return value >> 4


def load_calibration(calibration_file):
    calibration = json.loads(
        Path(calibration_file).read_text(encoding="utf-8")
    )
    # Upgrade calibration files produced by the first prototype version.
    if "z_offset" not in calibration and all(
        key in calibration for key in ("minimum", "maximum")
    ):
        upgraded = calibration_from_extrema(
            calibration["minimum"],
            calibration["maximum"],
        )
        calibration.update(
            {
                "z_offset": upgraded["z_offset"],
                "z_scale": upgraded["z_scale"],
            }
        )
    missing = [key for key in CALIBRATION_KEYS if key not in calibration]
    if missing:
        raise ValueError(
            "Compass calibration is missing: " + ", ".join(missing)
        )
    return calibration


def apply_calibration(values, calibration):
    return tuple(
        (value - float(calibration[f"{axis}_offset"]))
        * float(calibration[f"{axis}_scale"])
        for axis, value in zip("xyz", values)
    )


def calibration_from_extrema(minimum, maximum):
    radii = {
        axis: (float(maximum[axis]) - float(minimum[axis])) / 2.0
        for axis in "xyz"
    }
    invalid = [axis for axis, radius in radii.items() if radius <= 0]
    if invalid:
        raise ValueError(
            "Not enough movement to calibrate axes: " + ", ".join(invalid)
        )

    average_radius = sum(radii.values()) / len(radii)
    calibration = {}
    for axis in "xyz":
        calibration[f"{axis}_offset"] = (
            float(maximum[axis]) + float(minimum[axis])
        ) / 2.0
        calibration[f"{axis}_scale"] = average_radius / radii[axis]
    calibration["minimum"] = dict(minimum)
    calibration["maximum"] = dict(maximum)
    return calibration


class Lsm303Sensor:
    """Low-level access to the LSM303 accelerometer and magnetometer."""

    def __init__(self, bus_number=1, bus=None):
        if bus is None:
            from smbus import SMBus

            bus = SMBus(bus_number)
            self._owns_bus = True
        else:
            self._owns_bus = False
        self.bus = bus
        self._configure()

    def _configure(self):
        # Accelerometer: 10 Hz, high-resolution mode, ±2 g range.
        self.bus.write_byte_data(ACCELEROMETER, 0x20, 0x27)
        self.bus.write_byte_data(ACCELEROMETER, 0x23, 0x88)

        # Magnetometer: 30 Hz, ±1.3 gauss, continuous measurement mode.
        self.bus.write_byte_data(MAGNETOMETER, 0x00, 0x14)
        self.bus.write_byte_data(MAGNETOMETER, 0x01, 0x20)
        self.bus.write_byte_data(MAGNETOMETER, 0x02, 0x00)

    def read_accelerometer(self):
        data = self.bus.read_i2c_block_data(
            ACCELEROMETER,
            0x28 | 0x80,
            6,
        )
        return (
            signed_accelerometer_axis(data, 0),
            signed_accelerometer_axis(data, 2),
            signed_accelerometer_axis(data, 4),
        )

    def read_magnetometer(self):
        # The sensor returns six consecutive bytes in X, Z, Y order.
        data = self.bus.read_i2c_block_data(MAGNETOMETER, 0x03, 6)
        return (
            signed_big_endian(data[0], data[1]),
            signed_big_endian(data[4], data[5]),
            signed_big_endian(data[2], data[3]),
        )

    def close(self):
        if self._owns_bus and hasattr(self.bus, "close"):
            self.bus.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def calculate_orientation(mag_x, mag_y, mag_z, acc_x, acc_y, acc_z):
    heading_2d = math.degrees(math.atan2(mag_y, mag_x)) % 360.0

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
    heading = math.degrees(math.atan2(horizontal_y, horizontal_x)) % 360.0

    return Orientation(
        heading_2d=heading_2d,
        heading=heading,
        roll=math.degrees(roll),
        pitch=math.degrees(pitch),
    )


def map_telescope_position(orientation, settings):
    altitude_source = settings.get("altitude_source", "pitch")
    if altitude_source not in ("roll", "pitch"):
        raise ValueError("IMU altitude_source must be 'roll' or 'pitch'.")

    altitude_angle = getattr(orientation, altitude_source)
    altitude = (
        altitude_angle * float(settings.get("altitude_sign", 1.0))
        + float(settings.get("altitude_offset_deg", 0.0))
    )
    azimuth = (
        orientation.heading + float(settings.get("azimuth_offset_deg", 0.0))
    ) % 360.0
    return azimuth, max(-90.0, min(90.0, altitude))


class PositionSmoother:
    def __init__(self, time_constant_seconds=1.0, deadband_degrees=0.3):
        if time_constant_seconds < 0:
            raise ValueError("Smoothing time constant cannot be negative.")
        if deadband_degrees < 0:
            raise ValueError("Smoothing deadband cannot be negative.")

        self.time_constant = time_constant_seconds
        self.deadband = deadband_degrees
        self.azimuth = None
        self.altitude = None
        self.last_update = None

    def update(self, azimuth, altitude, now=None):
        if now is None:
            now = time.monotonic()

        if self.last_update is None:
            self.azimuth = azimuth % 360.0
            self.altitude = altitude
            self.last_update = now
            return self.azimuth, self.altitude

        elapsed = max(0.0, now - self.last_update)
        self.last_update = now
        alpha = (
            1.0
            if self.time_constant == 0
            else 1.0 - math.exp(-elapsed / self.time_constant)
        )

        azimuth_delta = (azimuth - self.azimuth + 180.0) % 360.0 - 180.0
        altitude_delta = altitude - self.altitude

        if abs(azimuth_delta) > self.deadband:
            self.azimuth = (self.azimuth + alpha * azimuth_delta) % 360.0
        if abs(altitude_delta) > self.deadband:
            self.altitude += alpha * altitude_delta

        return self.azimuth, self.altitude


class TelescopeImu:
    def __init__(self, calibration_file, settings, bus_number=1, sensor=None):
        self.settings = settings
        self.smoother = PositionSmoother(
            time_constant_seconds=float(
                settings.get("smoothing_time_constant_s", 1.0)
            ),
            deadband_degrees=float(settings.get("deadband_deg", 0.3)),
        )
        self.calibration = load_calibration(calibration_file)
        self.sensor = sensor or Lsm303Sensor(bus_number=bus_number)

    def read_accelerometer(self):
        return self.sensor.read_accelerometer()

    def read_magnetometer(self):
        return self.sensor.read_magnetometer()

    def read_orientation(self):
        acc_x, acc_y, acc_z = self.read_accelerometer()
        raw_x, raw_y, raw_z = self.read_magnetometer()
        corrected = apply_calibration(
            (raw_x, raw_y, raw_z),
            self.calibration,
        )
        return calculate_orientation(
            *corrected,
            acc_x,
            acc_y,
            acc_z,
        )

    def read_position(self):
        orientation = self.read_orientation()
        azimuth, altitude = map_telescope_position(
            orientation,
            self.settings,
        )
        azimuth, altitude = self.smoother.update(azimuth, altitude)
        return azimuth, altitude, orientation

    def close(self):
        self.sensor.close()
