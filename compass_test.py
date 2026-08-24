import math
import time
from smbus import SMBus

SENSOR = 0x1E
LCD = "/dev/ttyACM0"

bus = SMBus(1)

# Magnetómetro a 30 Hz
bus.write_byte_data(SENSOR, 0x00, 0x14)

# Rango magnético ±1,3 gauss
bus.write_byte_data(SENSOR, 0x01, 0x20)

# Medición continua
bus.write_byte_data(SENSOR, 0x02, 0x00)

display = open(LCD, "wb", buffering=0)
time.sleep(2)


def read_signed(high_register):
    high = bus.read_byte_data(SENSOR, high_register)
    low = bus.read_byte_data(SENSOR, high_register + 1)

    value = (high << 8) | low
    if value & 0x8000:
        value -= 65536

    return value


def show_lines(line1, line2):
    line1 = line1[:16].ljust(16)
    line2 = line2[:16].ljust(16)

    display.write(b"\xFE\x47\x01\x01")
    display.write(line1.encode("ascii"))

    display.write(b"\xFE\x47\x01\x02")
    display.write(line2.encode("ascii"))


try:
    while True:
        # El orden interno del sensor es X, Z, Y
        x = read_signed(0x03)
        z = read_signed(0x05)
        y = read_signed(0x07)

        heading = math.degrees(math.atan2(y, x))
        heading = (heading + 360.0) % 360.0

        show_lines(
            f"Rumbo {heading:6.1f}",
            f"X{x:+5d} Y{y:+5d}",
        )

        print(
            f"\rRumbo: {heading:6.1f}°  "
            f"X: {x:6d}  Y: {y:6d}  Z: {z:6d}",
            end="",
            flush=True,
        )

        time.sleep(0.25)

except KeyboardInterrupt:
    show_lines("Telescope", "Prueba detenida")
    print()

finally:
    display.close()
