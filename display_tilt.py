import math
import time
from smbus import SMBus

SENSOR = 0x19
LCD = "/dev/ttyACM0"

bus = SMBus(1)
bus.write_byte_data(SENSOR, 0x20, 0x27)
bus.write_byte_data(SENSOR, 0x23, 0x88)

display = open(LCD, "wb", buffering=0)
time.sleep(2)


def signed_axis(data, position):
    value = (data[position + 1] << 8) | data[position]
    if value & 0x8000:
        value -= 65536
    return value >> 4


def show_lines(line1, line2):
    line1 = line1[:16].ljust(16)
    line2 = line2[:16].ljust(16)

    display.write(b"\xFE\x47\x01\x01")
    display.write(line1.encode("ascii"))

    display.write(b"\xFE\x47\x01\x02")
    display.write(line2.encode("ascii"))


display.write(b"\xFE\x58")

try:
    while True:
        data = bus.read_i2c_block_data(SENSOR, 0x28 | 0x80, 6)

        x = signed_axis(data, 0)
        y = signed_axis(data, 2)
        z = signed_axis(data, 4)

        angle_x = math.degrees(
            math.atan2(x, math.sqrt(y * y + z * z))
        )
        angle_y = math.degrees(
            math.atan2(y, math.sqrt(x * x + z * z))
        )

        show_lines(
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
    show_lines("Telescope", "Test stopped")
    print()

finally:
    display.close()
