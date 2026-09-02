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
