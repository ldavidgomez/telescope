# LVGL Editor project

This directory is the editable source for the future Freenove FNK0104S user interface. It is intentionally separate from the working C/SDL prototype while the visual workflow is evaluated.

## Open it in VS Code

1. Open the repository root in VS Code. The extension detects this `ui` directory automatically.
2. Open `screens/guidance.xml`.
3. Run **LVGL: Open Editor** from the Command Palette if the Design view does not open automatically.
4. Select the `freenove-fnk0104s` target and switch to **Design** mode.

The labels use observable subjects from `globals.xml`, so the Raspberry Pi or ESP32 code can update values without rebuilding the visual hierarchy. The buttons already model brightness changes and day/night switching inside the preview.

The bundled Montserrat font files come from LVGL's official open-project template and are used at four rasterized sizes. They are generated at 2 bits per pixel to keep the eventual firmware footprint modest.

The empty `images` directory is kept in Git because LVGL Editor mounts it during resource conversion even when the interface does not yet use images.

The XML follows the format supported by LVGL Editor 1.0.1. The existing desktop simulator remains pinned to LVGL 9.4 until the generated UI is integrated.
