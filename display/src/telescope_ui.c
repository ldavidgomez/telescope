#include "telescope_ui.h"

#include <math.h>
#include <stdio.h>

#include "lvgl.h"

typedef struct {
    lv_obj_t *screen;
    lv_obj_t *target;
    lv_obj_t *az_arrow;
    lv_obj_t *alt_arrow;
    lv_obj_t *az_error;
    lv_obj_t *alt_error;
    lv_obj_t *current_position;
    lv_obj_t *target_position;
    lv_obj_t *status;
    lv_obj_t *buttons[3];
    lv_obj_t *theme_button_label;
} ui_objects_t;

static ui_objects_t ui;
static bool night_mode = true;
static int brightness_percent = 35;

static double shortest_angle(double target, double current)
{
    double difference = fmod(target - current + 540.0, 360.0) - 180.0;
    return difference;
}

static lv_color_t background_color(void)
{
    return night_mode ? lv_color_hex(0x080000) : lv_color_hex(0xEAF4FF);
}

static lv_color_t panel_color(void)
{
    return night_mode ? lv_color_hex(0x180000) : lv_color_hex(0xFFFFFF);
}

static lv_color_t primary_color(void)
{
    return night_mode ? lv_color_hex(0xFF2A1A) : lv_color_hex(0x1261A0);
}

static lv_color_t secondary_color(void)
{
    return night_mode ? lv_color_hex(0xA51B12) : lv_color_hex(0x537087);
}

static lv_color_t success_color(void)
{
    return night_mode ? lv_color_hex(0xFF584D) : lv_color_hex(0x16834A);
}

static void apply_theme(void)
{
    lv_obj_set_style_bg_color(ui.screen, background_color(), 0);
    lv_obj_set_style_bg_opa(ui.screen, LV_OPA_COVER, 0);

    lv_obj_t *panels[] = {
        lv_obj_get_parent(ui.az_arrow),
        lv_obj_get_parent(ui.alt_arrow),
        lv_obj_get_parent(ui.current_position),
    };
    for(size_t index = 0; index < sizeof(panels) / sizeof(panels[0]); ++index) {
        lv_obj_set_style_bg_color(panels[index], panel_color(), 0);
        lv_obj_set_style_border_color(panels[index], secondary_color(), 0);
    }

    lv_obj_t *primary_labels[] = {
        ui.target,
        ui.az_arrow,
        ui.alt_arrow,
        ui.az_error,
        ui.alt_error,
        ui.current_position,
        ui.target_position,
    };
    for(size_t index = 0; index < sizeof(primary_labels) / sizeof(primary_labels[0]); ++index) {
        lv_obj_set_style_text_color(primary_labels[index], primary_color(), 0);
    }

    lv_obj_set_style_text_color(ui.status, success_color(), 0);
    for(size_t index = 0; index < sizeof(ui.buttons) / sizeof(ui.buttons[0]); ++index) {
        lv_obj_set_style_bg_color(
            ui.buttons[index],
            night_mode ? lv_color_hex(0x36100D) : lv_color_hex(0x1261A0),
            0
        );
        lv_obj_set_style_text_color(ui.buttons[index], lv_color_hex(0xFFFFFF), 0);
    }
}

static void update_brightness_label(void)
{
    lv_label_set_text_fmt(
        ui.theme_button_label,
        "%s  |  %d%%",
        night_mode ? "DAY" : "NIGHT",
        brightness_percent
    );
    lv_obj_set_style_opa(ui.screen, (lv_opa_t)(90 + brightness_percent * 165 / 100), 0);
}

static void brightness_event(lv_event_t *event)
{
    int change = (int)(intptr_t)lv_event_get_user_data(event);
    brightness_percent += change;
    if(brightness_percent < 5) brightness_percent = 5;
    if(brightness_percent > 100) brightness_percent = 100;
    update_brightness_label();
}

static void theme_event(lv_event_t *event)
{
    (void)event;
    night_mode = !night_mode;
    apply_theme();
    update_brightness_label();
}

static lv_obj_t *create_panel(lv_obj_t *parent, int x, int y, int width, int height)
{
    lv_obj_t *panel = lv_obj_create(parent);
    lv_obj_set_pos(panel, x, y);
    lv_obj_set_size(panel, width, height);
    lv_obj_set_style_radius(panel, 12, 0);
    lv_obj_set_style_border_width(panel, 1, 0);
    lv_obj_set_style_pad_all(panel, 8, 0);
    lv_obj_clear_flag(panel, LV_OBJ_FLAG_SCROLLABLE);
    return panel;
}

static lv_obj_t *create_button(lv_obj_t *parent, const char *text, int x, int width)
{
    lv_obj_t *button = lv_button_create(parent);
    lv_obj_set_pos(button, x, 278);
    lv_obj_set_size(button, width, 34);
    lv_obj_set_style_radius(button, 9, 0);

    lv_obj_t *label = lv_label_create(button);
    lv_label_set_text(label, text);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_14, 0);
    lv_obj_center(label);
    return button;
}

void telescope_ui_create(void)
{
    ui.screen = lv_screen_active();
    lv_obj_remove_style_all(ui.screen);

    ui.target = lv_label_create(ui.screen);
    lv_label_set_text(ui.target, "ALDEBARAN");
    lv_obj_set_style_text_font(ui.target, &lv_font_montserrat_24, 0);
    lv_obj_set_pos(ui.target, 14, 8);

    ui.status = lv_label_create(ui.screen);
    lv_obj_set_style_text_font(ui.status, &lv_font_montserrat_12, 0);
    lv_obj_align(ui.status, LV_ALIGN_TOP_RIGHT, -14, 13);

    lv_obj_t *az_panel = create_panel(ui.screen, 12, 42, 222, 150);
    lv_obj_t *az_title = lv_label_create(az_panel);
    lv_label_set_text(az_title, "AZIMUTH");
    lv_obj_set_style_text_font(az_title, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(az_title, secondary_color(), 0);
    lv_obj_align(az_title, LV_ALIGN_TOP_MID, 0, 0);

    ui.az_arrow = lv_label_create(az_panel);
    lv_obj_set_style_text_font(ui.az_arrow, &lv_font_montserrat_48, 0);
    lv_obj_align(ui.az_arrow, LV_ALIGN_CENTER, 0, -5);

    ui.az_error = lv_label_create(az_panel);
    lv_obj_set_style_text_font(ui.az_error, &lv_font_montserrat_20, 0);
    lv_obj_align(ui.az_error, LV_ALIGN_BOTTOM_MID, 0, -2);

    lv_obj_t *alt_panel = create_panel(ui.screen, 246, 42, 222, 150);
    lv_obj_t *alt_title = lv_label_create(alt_panel);
    lv_label_set_text(alt_title, "ALTITUDE");
    lv_obj_set_style_text_font(alt_title, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(alt_title, secondary_color(), 0);
    lv_obj_align(alt_title, LV_ALIGN_TOP_MID, 0, 0);

    ui.alt_arrow = lv_label_create(alt_panel);
    lv_obj_set_style_text_font(ui.alt_arrow, &lv_font_montserrat_48, 0);
    lv_obj_align(ui.alt_arrow, LV_ALIGN_CENTER, 0, -5);

    ui.alt_error = lv_label_create(alt_panel);
    lv_obj_set_style_text_font(ui.alt_error, &lv_font_montserrat_20, 0);
    lv_obj_align(ui.alt_error, LV_ALIGN_BOTTOM_MID, 0, -2);

    lv_obj_t *position_panel = create_panel(ui.screen, 12, 202, 456, 66);
    ui.current_position = lv_label_create(position_panel);
    lv_obj_set_style_text_font(ui.current_position, &lv_font_montserrat_16, 0);
    lv_obj_align(ui.current_position, LV_ALIGN_TOP_LEFT, 0, 0);

    ui.target_position = lv_label_create(position_panel);
    lv_obj_set_style_text_font(ui.target_position, &lv_font_montserrat_16, 0);
    lv_obj_align(ui.target_position, LV_ALIGN_BOTTOM_LEFT, 0, 0);

    lv_obj_t *minus_button = create_button(ui.screen, "BRIGHT -", 12, 112);
    ui.buttons[0] = minus_button;
    lv_obj_add_event_cb(minus_button, brightness_event, LV_EVENT_CLICKED, (void *)(intptr_t)-10);

    lv_obj_t *theme_button = create_button(ui.screen, "", 134, 212);
    ui.buttons[1] = theme_button;
    ui.theme_button_label = lv_label_create(theme_button);
    lv_obj_set_style_text_font(ui.theme_button_label, &lv_font_montserrat_14, 0);
    lv_obj_center(ui.theme_button_label);
    lv_obj_add_event_cb(theme_button, theme_event, LV_EVENT_CLICKED, NULL);

    lv_obj_t *plus_button = create_button(ui.screen, "BRIGHT +", 356, 112);
    ui.buttons[2] = plus_button;
    lv_obj_add_event_cb(plus_button, brightness_event, LV_EVENT_CLICKED, (void *)(intptr_t)10);

    apply_theme();
    update_brightness_label();
}

void telescope_ui_set_state(const telescope_ui_state_t *state)
{
    double azimuth_error = shortest_angle(state->target_azimuth, state->current_azimuth);
    double altitude_error = state->target_altitude - state->current_altitude;
    bool aligned = fabs(azimuth_error) < 0.5 && fabs(altitude_error) < 0.5;

    lv_label_set_text(ui.target, state->target_name != NULL ? state->target_name : "WAITING FOR TARGET");
    lv_label_set_text(ui.az_arrow, fabs(azimuth_error) < 0.5 ? "OK" : (azimuth_error > 0 ? ">" : "<"));
    lv_label_set_text(ui.alt_arrow, fabs(altitude_error) < 0.5 ? "OK" : (altitude_error > 0 ? "^" : "v"));
    lv_label_set_text_fmt(ui.az_error, "%+.1f deg", azimuth_error);
    lv_label_set_text_fmt(ui.alt_error, "%+.1f deg", altitude_error);
    lv_label_set_text_fmt(
        ui.current_position,
        "CURRENT   AZ %06.1f    ALT %+05.1f",
        state->current_azimuth,
        state->current_altitude
    );
    lv_label_set_text_fmt(
        ui.target_position,
        "TARGET    AZ %06.1f    ALT %+05.1f",
        state->target_azimuth,
        state->target_altitude
    );
    lv_label_set_text_fmt(
        ui.status,
        "%s  ST %s  PI %s  IMU %s",
        aligned ? "ALIGNED" : "GUIDING",
        state->stellarium_connected ? "OK" : "--",
        state->raspberry_connected ? "OK" : "--",
        state->imu_ready ? "OK" : "--"
    );

    lv_obj_set_style_text_color(ui.az_arrow, aligned ? success_color() : primary_color(), 0);
    lv_obj_set_style_text_color(ui.alt_arrow, aligned ? success_color() : primary_color(), 0);
}
