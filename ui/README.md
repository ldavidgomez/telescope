# LVGL Editor project

This directory is the editable source for the future Freenove FNK0104S user interface. It is intentionally separate from the working C/SDL prototype while the visual workflow is evaluated.

## Open it in VS Code

1. Open the repository root in VS Code. The extension detects this `ui` directory automatically.
2. Open `screens/guidance.xml`.
3. Run **LVGL: Open Editor** from the Command Palette if the Design view does not open automatically.
4. Select the `freenove-fnk0104s` target and switch to **Design** mode.

The labels use observable subjects from `globals.xml`, so the Raspberry Pi or ESP32 code can update values without rebuilding the visual hierarchy. The buttons already model brightness changes and day/night switching inside the preview.

The main screen combines azimuth and altitude guidance into one reticle. The `guide_sector` subject selects one of eight arrow directions in the XML preview (`0` east through `7` north-east). During firmware integration this can be upgraded to a continuous angle, while the numeric AZ and ALT errors remain visible for precision and diagnostics.

Because the desktop preview has no physical backlight, brightness is represented by a non-interactive black overlay with discrete opacity levels. On the FNK0104S, the same `brightness` subject will drive the display backlight instead.

The bundled Montserrat font files come from LVGL's official open-project template and are used at five rasterized sizes. The 60 px variant is reserved for the two large direction indicators, while the 12 px variant keeps connection details compact. They are generated at 2 bits per pixel to keep the eventual firmware footprint modest.

The empty `images`, `widgets`, and `components` directories are kept in Git because LVGL Editor expects or scans them even when the interface does not yet use those resource types.

Preview binaries, build directories, editor caches, and the local project file are ignored. XML sources, exported C files, converted font data, and `file_list_gen.cmake` are committed so the firmware remains buildable and reviewable without regenerating the interface first.

The XML follows the format supported by LVGL Editor 1.0.1. The existing desktop simulator remains pinned to LVGL 9.4 until the generated UI is integrated.
