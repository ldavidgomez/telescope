import math
import time
from smbus import SMBus

ADDRESS = 0x19
bus = SMBus(1)

# 10 Hz with the X/Y/Z axes enabled
bus.write_byte_data(ADDRESS, 0x20, 0x27)

# High-resolution mode, ±2 g range
bus.write_byte_data(ADDRESS, 0x23, 0x88)


def signed_axis(data, position):
    value = (data[position + 1] << 8) | data[position]
    if value & 0x8000:
        value -= 65536
    return value >> 4


try:
    while True:
        data = bus.read_i2c_block_data(ADDRESS, 0x28 | 0x80, 6)

        x = signed_axis(data, 0)
        y = signed_axis(data, 2)
        z = signed_axis(data, 4)

        angle_x = math.degrees(
            math.atan2(x, math.sqrt(y * y + z * z))
        )
        angle_y = math.degrees(
            math.atan2(y, math.sqrt(x * x + z * z))
        )

        print(
            f"\rX: {x:5d}  Y: {y:5d}  Z: {z:5d}  "
            f"Ang X: {angle_x:6.1f}°  Ang Y: {angle_y:6.1f}°",
            end="",
            flush=True,
        )

        time.sleep(0.25)

except KeyboardInterrupt:
    print()
