# Project notes

## Validated prototype

The complete push-to workflow was validated on 2026-09-01 with a Raspberry Pi
Model B+ v1.2 and a OnePlus Nord 2T running Android 14:

- The IMU orientation is sampled with gyroscope-assisted fusion at 100 Hz.
- Stellarium Desktop uses the binary protocol on TCP port 10001.
- Stellarium Mobile Plus uses the LX200-compatible protocol on TCP port 10002.
- LX200 works both over Wi-Fi and over Bluetooth 2.0 SPP/RFCOMM channel 1.
- The mobile app reads the telescope pointer and can send target coordinates.
- The phone can synchronize date, time zone, latitude, and longitude.
- The LCD updates from both desktop and mobile connections and displays
  directional push-to guidance.
- The LCD also refreshes directly from the IMU every 0.5 seconds, without
  depending on a connected Stellarium client.
- LCD day/night color is controlled locally from solar altitude, with
  configurable twilight hysteresis and manual overrides.
- Bluetooth operation continues when Wi-Fi is disabled on the phone.
- The automated test suite contains 56 passing tests.
- The Python source is organized into the `telescope/` application package,
  `tools/` manual utilities, `tests/`, and `systemd/` deployment files.

## Known operational behavior

- The old Raspberry Pi can take several minutes to boot, start its services,
  and reconnect Wi-Fi. SD activity and Wi-Fi LEDs should be allowed to settle
  before diagnosing a failure.
- A location synchronized from Stellarium Mobile is kept in memory only. A
  service or Raspberry Pi restart restores the private configuration file.
- The CSR8510 adapter works with authenticated RFCOMM (`-A`), but forcing the
  legacy encryption flag (`-E`) caused `InputOutputError` on Android 14.
- Bluetooth discoverability lasts 180 seconds. Re-enable it before selecting a
  device in Stellarium if necessary.
- An incorrect pairing PIN after restarting or reconfiguring BlueZ indicates
  stale link keys. Forget the phone and Raspberry Pi bond on both sides and
  pair again with an interactive `bluetoothctl` agent.
- `Connected: no` in `bluetoothctl info` is normal while Stellarium is closed;
  RFCOMM connects only while the app is using the telescope.
- The RTL8188EUS adapter has been observed remaining associated with a strong
  signal and a valid DHCP lease while its IPv4 data path is unresponsive. The
  independent `telescope-wifi-watchdog.service` checks the current gateway
  through `wlan0` and reconnects the active NetworkManager profile after three
  failures among the five most recent probes. It does not restart the telescope
  or Bluetooth services.

## Pending power bank test

- Confirm that the 20,000 mAh, 22.5 W power bank provides 5 V at 2.5 A or
  more on the selected port; 5 V at 3 A is preferable.
- Use a short, good-quality micro-USB power cable.
- Test with the LCD, IMU, Wi-Fi adapter, and Bluetooth adapter connected.
- Repeat the field workflow with phone Wi-Fi disabled and Bluetooth connected.
- Run `vcgencmd get_throttled` after startup and again after several hours.
  The expected result is `throttled=0x0`.
- Check that the power bank does not switch itself off under a low load.

## Future battery telemetry

- Consider an inline USB meter that records accumulated Wh, current, voltage,
  and elapsed time.
- Calibrate the power bank's usable output energy before estimating a remaining
  percentage; its advertised 20,000 mAh rating refers to the internal cell
  voltage, not directly to the regulated 5 V output.
- Confirm that the meter does not introduce undervoltage by checking
  `vcgencmd get_throttled` with the complete telescope hardware connected.
- Direct software access to the power bank charge is out of scope for the
  current prototype.

## Graphical controller prototype

- A Freenove FNK0104S ESP32-S3 board with a 4-inch 320 x 480 capacitive display
  has been ordered. The intended installation uses it horizontally at 480 x
  320.
- A native LVGL 9.4 simulator now runs on macOS using SDL. It provides a first
  interactive guidance screen with simulated telescope movement, day/night
  themes, and brightness buttons.
- An LVGL Editor XML project lives in the repository-level `ui/` directory so
  the same 480 x 320 design can be edited visually and exported later.
- The interface is kept separate from the desktop simulation layer so it can
  be reused by the ESP32 firmware.
- The exact Freenove display, touch, backlight, and serial adapters remain
  pending until the physical board and its current vendor examples arrive.
- The Raspberry Pi will remain responsible for the IMU, astronomical
  calculations, and Stellarium protocols. The FNK0104S will render state sent
  by the Pi and return local touch commands.
