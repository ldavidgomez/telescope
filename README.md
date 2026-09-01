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

The IMU uses I2C bus 1 at addresses `0x19`, `0x1e`, `0x6b`, and `0x77`. The LCD
normally appears as `/dev/ttyACM0`.

## Project layout

- `astronomy.py`: J2000 and horizontal coordinate conversion.
- `configuration.py`: configuration loading and validation.
- `imu.py`: sensor access, calibration, orientation, mapping, and smoothing.
- `display.py`: fault-tolerant serial LCD access.
- `stellarium_protocol.py`: binary Stellarium protocol encoding and decoding.
- `stellarium_server.py`: network server and application coordination.
- `calibrate_compass.py`: magnetometer calibration tool.
- `record_imu.py`: synchronized nine-axis recording and gyro bias measurement.
- `replay_imu.py`: offline evaluation of gyroscope-assisted orientation.
- `compass_test.py`, `tilt_test.py`, `display_tilt.py`: hardware diagnostics.
- `telescope.service`: automatic systemd service.

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

The server listens on `telescope.local:10001`. Configure Stellarium Telescope
Control to use an external telescope server at that address and port.

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
in English.
