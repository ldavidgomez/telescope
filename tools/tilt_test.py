import math
import time

from telescope.imu import Lsm303Sensor


def tilt_angles(x, y, z):
    return (
        math.degrees(math.atan2(x, math.sqrt(y * y + z * z))),
        math.degrees(math.atan2(y, math.sqrt(x * x + z * z))),
    )


def main():
    with Lsm303Sensor() as sensor:
        try:
            while True:
                x, y, z = sensor.read_accelerometer()
                angle_x, angle_y = tilt_angles(x, y, z)
                print(
                    f"\rX: {x:5d}  Y: {y:5d}  Z: {z:5d}  "
                    f"Ang X: {angle_x:6.1f}°  Ang Y: {angle_y:6.1f}°",
                    end="",
                    flush=True,
                )
                time.sleep(0.25)
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    main()
