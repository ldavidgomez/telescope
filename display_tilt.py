import argparse
import time

from display import DEFAULT_LCD_DEVICE, LcdDisplay
from imu import Lsm303Sensor
from tilt_test import tilt_angles


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Show accelerometer tilt on the serial LCD."
    )
    parser.add_argument("--lcd", default=DEFAULT_LCD_DEVICE)
    return parser.parse_args()


def main():
    args = parse_arguments()
    with Lsm303Sensor() as sensor, LcdDisplay(args.lcd) as display:
        display.clear()
        try:
            while True:
                x, y, z = sensor.read_accelerometer()
                angle_x, angle_y = tilt_angles(x, y, z)
                display.show(
                    f"X {angle_x:+6.1f} deg",
                    f"Y {angle_y:+6.1f} deg",
                )
                print(
                    f"\rX: {angle_x:+6.1f}  Y: {angle_y:+6.1f}",
                    end="",
                    flush=True,
                )
                time.sleep(0.25)
        except KeyboardInterrupt:
            display.show("Telescope", "Test stopped")
            print()


if __name__ == "__main__":
    main()
