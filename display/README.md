# Telescope display simulator

This directory contains the first graphical interface for the Freenove FNK0104S display. It runs in a 480 x 320 desktop window and uses the mouse as the capacitive touchscreen.

The `src` directory is platform-independent LVGL code. The `simulator` directory only provides the macOS display and mouse. When the hardware arrives, a separate ESP32 entry point will replace the simulator without duplicating the interface.

## macOS requirements

Install the build tools once:

```sh
brew install cmake sdl2
```

## Run

From the repository root:

```sh
make display-run
```

The first build downloads the pinned LVGL source. Later builds use the local copy in `display/build`.

The demo gradually moves the simulated telescope towards Aldebaran. Click `BRIGHT -`, `BRIGHT +`, or `DAY`/`NIGHT` to test the touchscreen controls.

## VS Code

Open the repository and install the Microsoft C/C++ and CMake Tools extensions. Configure `display` as the CMake source directory and select the `telescope-display` target.

The simulator validates layout and interaction. Physical brightness, colour, touch behaviour, power consumption, and display-bus performance must be checked on the FNK0104S.

## Visual editing

The repository-level `ui` directory contains the same concept as an LVGL Editor XML project. Open the repository normally in VS Code, then open `ui/screens/guidance.xml` in Design mode. It is currently a visual prototype; the working C/SDL simulator remains the executable reference until the XML export has been verified and integrated.
