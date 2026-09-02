#ifndef TELESCOPE_UI_H
#define TELESCOPE_UI_H

#include <stdbool.h>

typedef struct {
    const char *target_name;
    double current_azimuth;
    double current_altitude;
    double target_azimuth;
    double target_altitude;
    bool stellarium_connected;
    bool imu_ready;
    bool raspberry_connected;
} telescope_ui_state_t;

void telescope_ui_create(void);
void telescope_ui_set_state(const telescope_ui_state_t *state);

#endif

