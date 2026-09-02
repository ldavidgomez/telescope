#ifndef _DEFAULT_SOURCE
#define _DEFAULT_SOURCE
#endif

#include <math.h>
#include <unistd.h>

#include "lvgl.h"
#include "telescope_ui.h"

static telescope_ui_state_t demo_state = {
    .target_name = "ALDEBARAN",
    .current_azimuth = 52.0,
    .current_altitude = 18.0,
    .target_azimuth = 67.4,
    .target_altitude = 31.8,
    .stellarium_connected = true,
    .imu_ready = true,
    .raspberry_connected = true,
};

static void demo_timer(lv_timer_t *timer)
{
    (void)timer;
    double azimuth_error = fmod(demo_state.target_azimuth - demo_state.current_azimuth + 540.0, 360.0) - 180.0;
    double altitude_error = demo_state.target_altitude - demo_state.current_altitude;

    if(fabs(azimuth_error) > 0.08) demo_state.current_azimuth += azimuth_error * 0.025;
    if(fabs(altitude_error) > 0.08) demo_state.current_altitude += altitude_error * 0.025;
    if(demo_state.current_azimuth < 0.0) demo_state.current_azimuth += 360.0;
    if(demo_state.current_azimuth >= 360.0) demo_state.current_azimuth -= 360.0;

    telescope_ui_set_state(&demo_state);
}

int main(void)
{
    lv_init();

    lv_display_t *display = lv_sdl_window_create(480, 320);
    lv_display_set_default(display);

    lv_indev_t *mouse = lv_sdl_mouse_create();
    lv_indev_set_display(mouse, display);

    telescope_ui_create();
    telescope_ui_set_state(&demo_state);
    lv_timer_create(demo_timer, 50, NULL);

    while(1) {
        uint32_t sleep_ms = lv_timer_handler();
        if(sleep_ms == LV_NO_TIMER_READY || sleep_ms > 20) sleep_ms = 20;
        usleep(sleep_ms * 1000);
    }
}

