# Telescope

A Raspberry Pi push-to assistant for a GSO 250/1250 Dobsonian telescope. It
reads an Adafruit 10-DOF IMU, exposes the current telescope position to
Stellarium, and shows the current position and target difference on a 16x2
serial LCD.

## Hardware

- Raspberry Pi Model B+ v1.2
- Adafruit 10-DOF IMU (L3GD20H + LSM303 + BMP180)
- Adafruit USB serial 16x2 RGB LCD
- RTL8188EUS USB Wi-Fi adapter
- CSR8510 USB Bluetooth adapter

The IMU uses I2C bus 1 at addresses `0x19`, `0x1e`, `0x6b`, and `0x77`. The LCD
normally appears as `/dev/ttyACM0`.

## Project layout

- `astronomy.py`: J2000 and horizontal coordinate conversion.
- `configuration.py`: configuration loading and validation.
- `imu.py`: sensor access, calibration, orientation, mapping, and smoothing.
- `display.py`: fault-tolerant serial LCD access.
- `stellarium_protocol.py`: binary Stellarium protocol encoding and decoding.
- `lx200_protocol.py`: LX200 command parsing and coordinate formatting.
- `stellarium_server.py`: network server and application coordination.
- `bluetooth_bridge.py`: Bluetooth serial to local LX200 TCP bridge.
- `wifi_watchdog.py`: recovery for an associated but unresponsive Wi-Fi link.
- `calibrate_compass.py`: magnetometer calibration tool.
- `record_imu.py`: synchronized nine-axis recording and gyro bias measurement.
- `replay_imu.py`: offline evaluation of gyroscope-assisted orientation.
- `compass_test.py`, `tilt_test.py`, `display_tilt.py`: hardware diagnostics.
- `telescope.service`: automatic systemd service.
- `telescope-bluetooth.service`: automatic RFCOMM-to-LX200 bridge service.
- `telescope-wifi-watchdog.service`: automatic Wi-Fi connectivity watchdog.

## Raspberry Pi preparation

Enable I2C and install the operating-system packages:

```bash
sudo apt install python3-smbus i2c-tools
```

The `astro` user must belong to the `i2c` and `dialout` groups. The service
adds these groups while it runs.

## Configuration

Copy `telescope_config.example.json` to `telescope_config.json` and set the
observer latitude and longitude. The real configuration and calibration files
are intentionally excluded from Git.

Important IMU settings:

- `altitude_source`: board axis used for telescope altitude (`roll` or `pitch`).
- `altitude_sign`: reverses that axis when set to `-1.0`.
- `altitude_offset_deg`: mechanical altitude correction.
- `azimuth_offset_deg`: mechanical heading correction.
- `smoothing_time_constant_s`: response smoothing; larger values move slower.
- `deadband_deg`: ignores movements smaller than this angle.
- `fusion_enabled`: enables the experimental gyroscope-assisted orientation.
- `fusion_sample_rate_hz`: internal fusion rate; use `100` for this hardware.
- `fusion_time_constant_s`: absolute-sensor correction time; `0.1` is the
  measured starting point for this telescope.
- `gyroscope_bias_dps`: stationary X, Y, and Z bias measured by
  `record_imu.py`.
- `gyroscope_signs`: maps the board axes to roll, pitch, and heading rates.

Fusion runs in a background sampling thread, so Stellarium can keep its lower
network update rate without losing fast gyroscope movement. Set
`fusion_enabled` to `false` to return immediately to the original
accelerometer-and-magnetometer calculation.

## Deploy and operate

Run these commands from the Mac:

```bash
make deploy
make deploy-config
make service-install
make service-permissions
make service-status
make service-logs
```

`make service-permissions` asks for the administrator password once. It installs
a narrowly scoped sudo rule that lets the `astro` user start, stop, and restart
only `telescope.service`, and follow only that service's log. It does not grant
general passwordless administrator access.

After changing the program, deploy and restart it with:

```bash
make service-update
```

The server listens on two ports and both connections share the same IMU,
target, and LCD guidance:

- `telescope.local:10001`: Stellarium desktop binary protocol.
- `telescope.local:10002`: LX200 protocol for Stellarium Mobile Plus.

Configure Stellarium Telescope Control on the Mac to use an external telescope
server on port `10001`. Port `10002` can also be used to test the mobile LX200
connection over Wi-Fi before enabling Bluetooth serial transport.

### Bluetooth connection for Android

The Android connection uses classic Bluetooth Serial Port Profile (SPP), not
Bluetooth networking. Install its independent service once:

```bash
make bluetooth-install
make bluetooth-status
```

The installation enables BlueZ compatibility mode so the Raspberry Pi can
publish an SPP service, then exposes RFCOMM channel 1 and bridges it only to the
local LX200 port. The phone must be paired and trusted before using the service.
In Stellarium Mobile Plus, add a telescope using the Meade LX200 protocol and
select the paired `telescope` Bluetooth device.

This CSR8510 adapter is authenticated with `rfcomm -A`. Explicit RFCOMM
encryption enforcement is not used because `rfcomm -E` caused Android 14 to
fail with `InputOutputError`; the phone must still be paired before it can
connect.

To pair a new Android phone, start an interactive agent on the Raspberry Pi:

```text
bluetoothctl
agent KeyboardDisplay
default-agent
pairable on
discoverable on
```

Select `telescope` in Android's Bluetooth settings, verify that both devices
show the same passkey, answer `yes` in `bluetoothctl`, and then trust the phone:

```text
trust PHONE_BLUETOOTH_ADDRESS
```

Discoverability expires after 180 seconds. Run `bluetoothctl discoverable on`
before opening Stellarium's Bluetooth device selector if `telescope` is not
listed. If Android reports an incorrect pairing PIN, remove or forget the bond
on both devices and pair them again; stale link keys cannot be repaired from
only one side.

The Bluetooth bridge is deliberately separate from `telescope.service`. A
Bluetooth or phone failure therefore cannot stop IMU sampling, LCD guidance, or
the existing Wi-Fi connections.

### Wi-Fi recovery watchdog

The RTL8188EUS adapter can occasionally remain associated with the access
point while its data path is no longer usable. Install the independent
watchdog once:

```bash
make wifi-watchdog-install
make wifi-watchdog-status
```

Every 20 seconds it sends three pings to the current IPv4 gateway explicitly
through `wlan0`; one reply is enough for that probe to pass. Three failed
probes among the five most recent checks trigger a
NetworkManager reconnection of the connection that was active. This also
detects an intermittent link that occasionally lets one probe through. It does
not restart the Raspberry Pi,
`telescope.service`, or the Bluetooth bridge. If Wi-Fi is intentionally
disconnected or no IPv4 gateway exists, the watchdog waits and lets
NetworkManager handle normal reconnection.

Follow recovery events with:

```bash
make wifi-watchdog-logs
```

The gateway and NetworkManager connection name are discovered dynamically, so
the same service can be used with a home router or a previously configured
phone hotspot. A DHCP reservation is still recommended because reconnecting
may otherwise change the Raspberry Pi address.

### Field operation with Stellarium Mobile Plus

The validated cable-free data path is:

```text
IMU -> Raspberry Pi -> LX200 TCP localhost:10002 -> Bluetooth SPP -> Android
```

In Stellarium Mobile Plus:

1. Select a Bluetooth telescope connection and the paired `telescope` device.
2. Let the app auto-detect the LX200-compatible controller.
3. Synchronize time and location.
4. Select an object and send the GoTo command.
5. Move the Dobsonian manually by following the LCD arrows.

The server accepts the phone's location and immediately uses it for coordinate
conversion. This location is intentionally session-only: restarting
`telescope.service` restores the observer coordinates from
`telescope_config.json`, so synchronize again after a service or Raspberry Pi
restart. The Raspberry Pi keeps its own system clock; Stellarium can read and
confirm its date, local time, and UTC offset.

For a final offline check, disable Wi-Fi on the phone while keeping Bluetooth
enabled. The telescope pointer, target commands, synchronized observer data,
and LCD guidance must continue to work.

Useful Bluetooth diagnostics on the Raspberry Pi:

```bash
systemctl status telescope-bluetooth.service
sudo journalctl -u telescope-bluetooth.service -f
rfcomm -a
bluetoothctl info PHONE_BLUETOOTH_ADDRESS
```

When a target is selected, the LCD guidance line uses `<` and `>` for azimuth,
`^` and `v` for altitude, and shows `OK` when an axis is within 0.5 degrees of
the target. The remaining angular distance stays visible beside each symbol.

## Calibration and diagnostics

Calibration must be performed after the IMU is mounted because nearby metal can
change the magnetic measurements. The Make targets stop the automatic service
before accessing the hardware and start it again when the tool exits:

```bash
make calibrate
make compass-test
```

Both commands use the LCD by default. The Python tools also support `--no-lcd`
when run directly on the Raspberry Pi.

### Nine-axis recording

Record a dataset for comparing the current orientation calculation with future
sensor-fusion algorithms:

```bash
make record-imu
make fetch-imu
```

Keep the IMU completely still during the one-second gyroscope warm-up and the
following two seconds while the L3GD20H bias is measured. After that, move it
through the test orientations.
The default recording is 30 seconds at 100 Hz. Different values can be selected
without editing the Makefile:

```bash
make record-imu RECORD_SECONDS=60 RECORD_RATE=50
```

The Raspberry Pi writes `imu_recording.csv` with raw and corrected readings for
all nine axes, plus the current tilt-compensated orientation. A companion
`imu_recording.json` stores the measured gyro bias and actual sample rate. Both
files are ignored by Git.

Replay the latest recording through the experimental complementary filter:

```bash
make replay-imu
```

This creates `imu_replay.csv` without changing the live Stellarium service.
The default 0.1-second correction time was selected from a controlled test
containing separate azimuth and altitude movements with stationary pauses.

## Development

The calculation and protocol tests do not require Raspberry Pi hardware:

```bash
make test
```

Hardware access is delayed until a sensor object is created, so modules and
tests can be imported on macOS. Runtime messages and code comments are written
in English. The current suite contains 48 automated tests covering astronomy,
configuration, sensor fusion, Stellarium's binary protocol, LX200, LCD
guidance, recording, mobile synchronization, and Wi-Fi recovery behavior.
