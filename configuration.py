import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Observer:
    latitude_deg: float
    longitude_deg: float
    altitude_m: float = 0.0

    @property
    def coordinates(self):
        return self.latitude_deg, self.longitude_deg


@dataclass(frozen=True)
class TelescopeConfig:
    observer: Observer
    imu: dict


def config_from_dict(data):
    observer_data = data["observer"]
    observer = Observer(
        latitude_deg=float(observer_data["latitude_deg"]),
        longitude_deg=float(observer_data["longitude_deg"]),
        altitude_m=float(observer_data.get("altitude_m", 0.0)),
    )
    if not -90.0 <= observer.latitude_deg <= 90.0:
        raise ValueError("Observer latitude must be between -90 and +90 degrees.")
    if not -180.0 <= observer.longitude_deg <= 180.0:
        raise ValueError(
            "Observer longitude must be between -180 and +180 degrees."
        )

    imu = dict(data["imu"])
    altitude_source = imu.get("altitude_source", "pitch")
    if altitude_source not in ("roll", "pitch"):
        raise ValueError("IMU altitude_source must be 'roll' or 'pitch'.")
    for setting in (
        "altitude_sign",
        "altitude_offset_deg",
        "azimuth_offset_deg",
        "smoothing_time_constant_s",
        "deadband_deg",
        "fusion_time_constant_s",
        "fusion_sample_rate_hz",
    ):
        if setting in imu:
            imu[setting] = float(imu[setting])
    if imu.get("smoothing_time_constant_s", 1.0) < 0:
        raise ValueError("Smoothing time constant cannot be negative.")
    if imu.get("deadband_deg", 0.3) < 0:
        raise ValueError("Smoothing deadband cannot be negative.")
    if imu.get("fusion_time_constant_s", 0.1) < 0:
        raise ValueError("Fusion time constant cannot be negative.")
    if imu.get("fusion_sample_rate_hz", 100.0) <= 0:
        raise ValueError("Fusion sample rate must be greater than zero.")
    if imu.get("fusion_sample_rate_hz", 100.0) not in (10.0, 50.0, 100.0):
        raise ValueError("Fusion sample rate must be 10, 50, or 100 Hz.")

    fusion_enabled = imu.get("fusion_enabled", False)
    if not isinstance(fusion_enabled, bool):
        raise ValueError("IMU fusion_enabled must be true or false.")
    if fusion_enabled and "gyroscope_bias_dps" not in imu:
        raise ValueError(
            "IMU gyroscope_bias_dps is required when fusion is enabled."
        )
    for setting, default in (
        ("gyroscope_bias_dps", None),
        ("gyroscope_signs", (1.0, -1.0, -1.0)),
    ):
        values = imu.get(setting, default)
        if values is None:
            continue
        if not isinstance(values, (list, tuple)) or len(values) != 3:
            raise ValueError(f"IMU {setting} must contain X, Y, and Z values.")
        imu[setting] = tuple(float(value) for value in values)

    return TelescopeConfig(observer=observer, imu=imu)


def load_config(config_file):
    data = json.loads(Path(config_file).read_text(encoding="utf-8"))
    return config_from_dict(data)
