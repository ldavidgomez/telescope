/**
 * @file telescope_ui_gen.h
 */

#ifndef TELESCOPE_UI_GEN_H
#define TELESCOPE_UI_GEN_H

#ifndef UI_SUBJECT_STRING_LENGTH
#define UI_SUBJECT_STRING_LENGTH 256
#endif

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/

#ifdef LV_LVGL_H_INCLUDE_SIMPLE
    #include "lvgl.h"
#else
    #include "lvgl/lvgl.h"
#endif

/*********************
 *      DEFINES
 *********************/

#define NIGHT_BG lv_color_hex(0x080000)

#define NIGHT_PANEL lv_color_hex(0x160000)

#define NIGHT_BORDER lv_color_hex(0x5E1010)

#define NIGHT_TEXT lv_color_hex(0xFF5A4F)

#define NIGHT_MUTED lv_color_hex(0xB12B26)

#define NIGHT_ACCENT lv_color_hex(0xFF2D20)

#define DAY_BG lv_color_hex(0x0C1720)

#define DAY_PANEL lv_color_hex(0x172935)

#define DAY_BORDER lv_color_hex(0x315568)

#define DAY_TEXT lv_color_hex(0xEAF7FF)

#define DAY_MUTED lv_color_hex(0x91ADBC)

#define DAY_ACCENT lv_color_hex(0x4DD5FF)

#define BRIGHTNESS_MASK lv_color_hex(0x000000)

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 * GLOBAL VARIABLES
 **********************/

/*-------------------
 * Permanent screens
 *------------------*/

extern lv_obj_t * guidance;

/*----------------
 * Global styles
 *----------------*/

extern lv_style_t screen_night;
extern lv_style_t screen_day;
extern lv_style_t panel_night;
extern lv_style_t panel_day;
extern lv_style_t muted_night;
extern lv_style_t muted_day;
extern lv_style_t accent_night;
extern lv_style_t accent_day;
extern lv_style_t value_night;
extern lv_style_t value_day;
extern lv_style_t button_night;
extern lv_style_t button_day;
extern lv_style_t guide_night;
extern lv_style_t guide_day;
extern lv_style_t transparent;
extern lv_style_t reticle_night;
extern lv_style_t reticle_day;
extern lv_style_t axis_night;
extern lv_style_t axis_day;
extern lv_style_t vector_night;
extern lv_style_t vector_day;
extern lv_style_t vector_dot_night;
extern lv_style_t vector_dot_day;
extern lv_style_t vector_line_pivot;
extern lv_style_t vector_angle_e;
extern lv_style_t vector_angle_se;
extern lv_style_t vector_angle_s;
extern lv_style_t vector_angle_sw;
extern lv_style_t vector_angle_w;
extern lv_style_t vector_angle_nw;
extern lv_style_t vector_angle_n;
extern lv_style_t vector_angle_ne;
extern lv_style_t vector_coarse;
extern lv_style_t vector_fine;
extern lv_style_t vector_aligned;
extern lv_style_t state_hidden;
extern lv_style_t state_visible;
extern lv_style_t brightness_10;
extern lv_style_t brightness_20;
extern lv_style_t brightness_30;
extern lv_style_t brightness_40;
extern lv_style_t brightness_50;
extern lv_style_t brightness_60;
extern lv_style_t brightness_70;
extern lv_style_t brightness_80;
extern lv_style_t brightness_90;
extern lv_style_t brightness_100;

/*----------------
 * Fonts
 *----------------*/

extern lv_font_t * font_small;

extern lv_font_t * font_body;

extern lv_font_t * font_heading;

extern lv_font_t * font_value;

/*----------------
 * Images
 *----------------*/

/*----------------
 * Subjects
 *----------------*/

extern lv_subject_t night_mode;
extern lv_subject_t brightness;
extern lv_subject_t target_name;
extern lv_subject_t current_az;
extern lv_subject_t current_alt;
extern lv_subject_t target_az;
extern lv_subject_t target_alt;
extern lv_subject_t az_direction;
extern lv_subject_t alt_direction;
extern lv_subject_t az_error;
extern lv_subject_t alt_error;
extern lv_subject_t guide_sector;
extern lv_subject_t guide_stage;
extern lv_subject_t guide_status;
extern lv_subject_t connection_status;

/**********************
 * GLOBAL PROTOTYPES
 **********************/

/*----------------
 * Event Callbacks
 *----------------*/

/**
 * Initialize the component library
 */

void telescope_ui_init_gen(const char * asset_path);

/**********************
 *      MACROS
 **********************/

/**********************
 *   POST INCLUDES
 **********************/

/*Include all the widget and components of this library*/
#include "screens/guidance_gen.h"

#ifdef __cplusplus
} /*extern "C"*/
#endif

#endif /*TELESCOPE_UI_GEN_H*/