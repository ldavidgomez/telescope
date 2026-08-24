# Project notes

## Pending power bank test

- Confirm that the 20,000 mAh, 22.5 W power bank provides 5 V at 2.5 A or more on the selected port; 5 V at 3 A is preferable.
- Use a short, good-quality micro-USB power cable.
- Test with the LCD, IMU, and Wi-Fi adapter connected.
- Run `vcgencmd get_throttled` after startup and again after several hours. The expected result is `throttled=0x0`.
- Check that the power bank does not switch itself off under a low load.
