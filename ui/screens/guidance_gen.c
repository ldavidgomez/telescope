/**
 * @file guidance_gen.c
 * @brief Template source file for LVGL objects
 */

/*********************
 *      INCLUDES
 *********************/

#include "guidance_gen.h"
#include "telescope_ui.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/***********************
 *  STATIC VARIABLES
 **********************/

/***********************
 *  STATIC PROTOTYPES
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

lv_obj_t * guidance_create(void)
{
    LV_TRACE_OBJ_CREATE("begin");


    static bool style_inited = false;

    if (!style_inited) {

        style_inited = true;
    }

    if (guidance == NULL) guidance = lv_obj_create(NULL);
    lv_obj_t * lv_obj_0 = guidance;
    lv_obj_set_name_static(lv_obj_0, "guidance_#");
    lv_obj_set_width(lv_obj_0, lv_pct(100));
    lv_obj_set_height(lv_obj_0, lv_pct(100));
    lv_obj_set_flag(lv_obj_0, LV_OBJ_FLAG_SCROLLABLE, false);

    lv_obj_add_style(lv_obj_0, &screen_night, 0);
    lv_obj_bind_style(lv_obj_0, &screen_day, 0, &night_mode, 0);
    lv_obj_t * lv_label_0 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_0, 10);
    lv_obj_set_y(lv_label_0, 7);
    lv_obj_set_width(lv_label_0, 330);
    lv_label_bind_text(lv_label_0, &target_name, NULL);
    lv_obj_set_style_text_font(lv_label_0, font_heading, 0);
    lv_label_set_long_mode(lv_label_0, LV_LABEL_LONG_MODE_DOTS);
    
    lv_obj_t * lv_label_1 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_1, 344);
    lv_obj_set_y(lv_label_1, 9);
    lv_obj_set_width(lv_label_1, 126);
    lv_label_bind_text(lv_label_1, &guide_status, NULL);
    lv_obj_set_style_text_align(lv_label_1, LV_TEXT_ALIGN_RIGHT, 0);
    lv_obj_add_style(lv_label_1, &accent_night, 0);
    lv_obj_bind_style(lv_label_1, &accent_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_2 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_2, 10);
    lv_obj_set_y(lv_label_2, 32);
    lv_obj_set_width(lv_label_2, 460);
    lv_label_bind_text(lv_label_2, &connection_status, NULL);
    lv_obj_set_style_text_font(lv_label_2, font_small, 0);
    lv_label_set_long_mode(lv_label_2, LV_LABEL_LONG_MODE_DOTS);
    lv_obj_add_style(lv_label_2, &muted_night, 0);
    lv_obj_bind_style(lv_label_2, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_1 = lv_obj_create(lv_obj_0);
    lv_obj_set_x(lv_obj_1, 8);
    lv_obj_set_y(lv_obj_1, 52);
    lv_obj_set_width(lv_obj_1, 300);
    lv_obj_set_height(lv_obj_1, 208);
    lv_obj_set_flag(lv_obj_1, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_1, &panel_night, 0);
    lv_obj_bind_style(lv_obj_1, &panel_day, 0, &night_mode, 0);
    lv_obj_t * lv_label_3 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_3, 0);
    lv_obj_set_y(lv_label_3, 0);
    lv_label_set_text(lv_label_3, "MOVE THIS WAY");
    lv_obj_set_style_text_font(lv_label_3, font_small, 0);
    lv_obj_add_style(lv_label_3, &muted_night, 0);
    lv_obj_bind_style(lv_label_3, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_2 = lv_obj_create(lv_obj_1);
    lv_obj_set_x(lv_obj_2, 60);
    lv_obj_set_y(lv_obj_2, 24);
    lv_obj_set_width(lv_obj_2, 160);
    lv_obj_set_height(lv_obj_2, 160);
    lv_obj_set_flag(lv_obj_2, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_2, &reticle_night, 0);
    lv_obj_bind_style(lv_obj_2, &reticle_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_3 = lv_obj_create(lv_obj_1);
    lv_obj_set_x(lv_obj_3, 60);
    lv_obj_set_y(lv_obj_3, 103);
    lv_obj_set_width(lv_obj_3, 160);
    lv_obj_set_height(lv_obj_3, 2);
    lv_obj_set_flag(lv_obj_3, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_3, &axis_night, 0);
    lv_obj_bind_style(lv_obj_3, &axis_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_4 = lv_obj_create(lv_obj_1);
    lv_obj_set_x(lv_obj_4, 139);
    lv_obj_set_y(lv_obj_4, 24);
    lv_obj_set_width(lv_obj_4, 2);
    lv_obj_set_height(lv_obj_4, 160);
    lv_obj_set_flag(lv_obj_4, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_4, &axis_night, 0);
    lv_obj_bind_style(lv_obj_4, &axis_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_5 = lv_obj_create(lv_obj_1);
    lv_obj_set_x(lv_obj_5, 140);
    lv_obj_set_y(lv_obj_5, 102);
    lv_obj_set_width(lv_obj_5, 88);
    lv_obj_set_height(lv_obj_5, 5);
    lv_obj_set_flag(lv_obj_5, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_5, &vector_night, 0);
    lv_obj_bind_style(lv_obj_5, &vector_day, 0, &night_mode, 0);
    lv_obj_add_style(lv_obj_5, &vector_line_pivot, 0);
    lv_obj_add_style(lv_obj_5, &vector_angle_ne, 0);
    lv_obj_add_style(lv_obj_5, &vector_coarse, 0);
    lv_obj_bind_style(lv_obj_5, &vector_fine, 0, &guide_stage, 1);
    lv_obj_bind_style(lv_obj_5, &vector_aligned, 0, &guide_stage, 2);
    lv_obj_bind_style(lv_obj_5, &vector_angle_e, 0, &guide_sector, 0);
    lv_obj_bind_style(lv_obj_5, &vector_angle_se, 0, &guide_sector, 1);
    lv_obj_bind_style(lv_obj_5, &vector_angle_s, 0, &guide_sector, 2);
    lv_obj_bind_style(lv_obj_5, &vector_angle_sw, 0, &guide_sector, 3);
    lv_obj_bind_style(lv_obj_5, &vector_angle_w, 0, &guide_sector, 4);
    lv_obj_bind_style(lv_obj_5, &vector_angle_nw, 0, &guide_sector, 5);
    lv_obj_bind_style(lv_obj_5, &vector_angle_n, 0, &guide_sector, 6);
    
    lv_obj_t * lv_obj_6 = lv_obj_create(lv_obj_1);
    lv_obj_set_x(lv_obj_6, 134);
    lv_obj_set_y(lv_obj_6, 98);
    lv_obj_set_width(lv_obj_6, 12);
    lv_obj_set_height(lv_obj_6, 12);
    lv_obj_set_flag(lv_obj_6, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_6, &vector_dot_night, 0);
    lv_obj_bind_style(lv_obj_6, &vector_dot_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_4 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_4, 80);
    lv_obj_set_y(lv_label_4, 92);
    lv_obj_set_width(lv_label_4, 120);
    lv_label_set_text(lv_label_4, "ALIGNED");
    lv_obj_set_style_text_font(lv_label_4, font_heading, 0);
    lv_obj_set_style_text_align(lv_label_4, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_add_style(lv_label_4, &state_hidden, 0);
    lv_obj_add_style(lv_label_4, &accent_night, 0);
    lv_obj_bind_style(lv_label_4, &state_visible, 0, &guide_stage, 2);
    lv_obj_bind_style(lv_label_4, &accent_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_7 = lv_obj_create(lv_obj_0);
    lv_obj_set_x(lv_obj_7, 314);
    lv_obj_set_y(lv_obj_7, 52);
    lv_obj_set_width(lv_obj_7, 158);
    lv_obj_set_height(lv_obj_7, 208);
    lv_obj_set_flag(lv_obj_7, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_7, &panel_night, 0);
    lv_obj_bind_style(lv_obj_7, &panel_day, 0, &night_mode, 0);
    lv_obj_t * lv_label_5 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_5, 0);
    lv_obj_set_y(lv_label_5, 0);
    lv_label_set_text(lv_label_5, "REMAINING");
    lv_obj_set_style_text_font(lv_label_5, font_small, 0);
    lv_obj_add_style(lv_label_5, &muted_night, 0);
    lv_obj_bind_style(lv_label_5, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_6 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_6, 0);
    lv_obj_set_y(lv_label_6, 24);
    lv_label_set_text(lv_label_6, "AZ");
    lv_obj_set_style_text_font(lv_label_6, font_small, 0);
    lv_obj_add_style(lv_label_6, &muted_night, 0);
    lv_obj_bind_style(lv_label_6, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_7 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_7, 0);
    lv_obj_set_y(lv_label_7, 39);
    lv_obj_set_width(lv_label_7, 138);
    lv_label_bind_text(lv_label_7, &az_error, NULL);
    lv_obj_set_style_text_font(lv_label_7, font_heading, 0);
    lv_obj_set_style_text_align(lv_label_7, LV_TEXT_ALIGN_RIGHT, 0);
    lv_obj_add_style(lv_label_7, &value_night, 0);
    lv_obj_bind_style(lv_label_7, &value_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_8 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_8, 0);
    lv_obj_set_y(lv_label_8, 71);
    lv_label_set_text(lv_label_8, "ALT");
    lv_obj_set_style_text_font(lv_label_8, font_small, 0);
    lv_obj_add_style(lv_label_8, &muted_night, 0);
    lv_obj_bind_style(lv_label_8, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_9 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_9, 0);
    lv_obj_set_y(lv_label_9, 86);
    lv_obj_set_width(lv_label_9, 138);
    lv_label_bind_text(lv_label_9, &alt_error, NULL);
    lv_obj_set_style_text_font(lv_label_9, font_heading, 0);
    lv_obj_set_style_text_align(lv_label_9, LV_TEXT_ALIGN_RIGHT, 0);
    lv_obj_add_style(lv_label_9, &value_night, 0);
    lv_obj_bind_style(lv_label_9, &value_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_10 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_10, 0);
    lv_obj_set_y(lv_label_10, 126);
    lv_label_set_text(lv_label_10, "NOW");
    lv_obj_set_style_text_font(lv_label_10, font_small, 0);
    lv_obj_add_style(lv_label_10, &muted_night, 0);
    lv_obj_bind_style(lv_label_10, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_11 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_11, 38);
    lv_obj_set_y(lv_label_11, 126);
    lv_obj_set_width(lv_label_11, 48);
    lv_label_bind_text(lv_label_11, &current_az, NULL);
    lv_obj_set_style_text_font(lv_label_11, font_small, 0);
    lv_obj_set_style_text_align(lv_label_11, LV_TEXT_ALIGN_RIGHT, 0);
    
    lv_obj_t * lv_label_12 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_12, 90);
    lv_obj_set_y(lv_label_12, 126);
    lv_obj_set_width(lv_label_12, 48);
    lv_label_bind_text(lv_label_12, &current_alt, NULL);
    lv_obj_set_style_text_font(lv_label_12, font_small, 0);
    lv_obj_set_style_text_align(lv_label_12, LV_TEXT_ALIGN_RIGHT, 0);
    
    lv_obj_t * lv_label_13 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_13, 0);
    lv_obj_set_y(lv_label_13, 158);
    lv_label_set_text(lv_label_13, "TGT");
    lv_obj_set_style_text_font(lv_label_13, font_small, 0);
    lv_obj_add_style(lv_label_13, &muted_night, 0);
    lv_obj_bind_style(lv_label_13, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_14 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_14, 38);
    lv_obj_set_y(lv_label_14, 158);
    lv_obj_set_width(lv_label_14, 48);
    lv_label_bind_text(lv_label_14, &target_az, NULL);
    lv_obj_set_style_text_font(lv_label_14, font_small, 0);
    lv_obj_set_style_text_align(lv_label_14, LV_TEXT_ALIGN_RIGHT, 0);
    
    lv_obj_t * lv_label_15 = lv_label_create(lv_obj_7);
    lv_obj_set_x(lv_label_15, 90);
    lv_obj_set_y(lv_label_15, 158);
    lv_obj_set_width(lv_label_15, 48);
    lv_label_bind_text(lv_label_15, &target_alt, NULL);
    lv_obj_set_style_text_font(lv_label_15, font_small, 0);
    lv_obj_set_style_text_align(lv_label_15, LV_TEXT_ALIGN_RIGHT, 0);
    
    lv_obj_t * lv_button_0 = lv_button_create(lv_obj_0);
    lv_obj_set_x(lv_button_0, 8);
    lv_obj_set_y(lv_button_0, 264);
    lv_obj_set_width(lv_button_0, 52);
    lv_obj_set_height(lv_button_0, 48);
    lv_obj_add_style(lv_button_0, &button_night, 0);
    lv_obj_bind_style(lv_button_0, &button_day, 0, &night_mode, 0);
    lv_subject_increment_dsc_t * subject_increment_event_0 = lv_obj_add_subject_increment_event(lv_button_0, &brightness, LV_EVENT_CLICKED, -10);
    lv_obj_set_subject_increment_event_min_value(lv_button_0, subject_increment_event_0, 10);
    lv_obj_set_subject_increment_event_max_value(lv_button_0, subject_increment_event_0, 100);
    lv_obj_t * lv_label_16 = lv_label_create(lv_button_0);
    lv_label_set_text(lv_label_16, "-");
    lv_obj_set_style_text_font(lv_label_16, font_heading, 0);
    lv_obj_set_align(lv_label_16, LV_ALIGN_CENTER);
    
    lv_obj_t * lv_label_17 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_17, 64);
    lv_obj_set_y(lv_label_17, 280);
    lv_obj_set_width(lv_label_17, 48);
    lv_label_bind_text(lv_label_17, &brightness, NULL);
    lv_obj_set_style_text_align(lv_label_17, LV_TEXT_ALIGN_RIGHT, 0);
    
    lv_obj_t * lv_label_18 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_18, 114);
    lv_obj_set_y(lv_label_18, 280);
    lv_label_set_text(lv_label_18, "%");
    
    lv_obj_t * lv_button_1 = lv_button_create(lv_obj_0);
    lv_obj_set_x(lv_button_1, 135);
    lv_obj_set_y(lv_button_1, 264);
    lv_obj_set_width(lv_button_1, 52);
    lv_obj_set_height(lv_button_1, 48);
    lv_obj_add_style(lv_button_1, &button_night, 0);
    lv_obj_bind_style(lv_button_1, &button_day, 0, &night_mode, 0);
    lv_subject_increment_dsc_t * subject_increment_event_1 = lv_obj_add_subject_increment_event(lv_button_1, &brightness, LV_EVENT_CLICKED, 10);
    lv_obj_set_subject_increment_event_min_value(lv_button_1, subject_increment_event_1, 10);
    lv_obj_set_subject_increment_event_max_value(lv_button_1, subject_increment_event_1, 100);
    lv_obj_t * lv_label_19 = lv_label_create(lv_button_1);
    lv_label_set_text(lv_label_19, "+");
    lv_obj_set_style_text_font(lv_label_19, font_heading, 0);
    lv_obj_set_align(lv_label_19, LV_ALIGN_CENTER);
    
    lv_obj_t * lv_button_2 = lv_button_create(lv_obj_0);
    lv_obj_set_x(lv_button_2, 318);
    lv_obj_set_y(lv_button_2, 264);
    lv_obj_set_width(lv_button_2, 154);
    lv_obj_set_height(lv_button_2, 48);
    lv_obj_add_style(lv_button_2, &button_night, 0);
    lv_obj_bind_style(lv_button_2, &button_day, 0, &night_mode, 0);
    lv_subject_increment_dsc_t * subject_increment_event_2 = lv_obj_add_subject_increment_event(lv_button_2, &night_mode, LV_EVENT_CLICKED, 1);
    lv_obj_set_subject_increment_event_min_value(lv_button_2, subject_increment_event_2, 0);
    lv_obj_set_subject_increment_event_max_value(lv_button_2, subject_increment_event_2, 1);
    lv_obj_set_subject_increment_event_rollover(lv_button_2, subject_increment_event_2, true);
    lv_obj_t * lv_label_20 = lv_label_create(lv_button_2);
    lv_label_set_text(lv_label_20, "DAY / NIGHT");
    lv_obj_set_align(lv_label_20, LV_ALIGN_CENTER);
    
    lv_obj_t * lv_obj_8 = lv_obj_create(lv_obj_0);
    lv_obj_set_x(lv_obj_8, 0);
    lv_obj_set_y(lv_obj_8, 0);
    lv_obj_set_width(lv_obj_8, lv_pct(100));
    lv_obj_set_height(lv_obj_8, lv_pct(100));
    lv_obj_set_flag(lv_obj_8, LV_OBJ_FLAG_CLICKABLE, false);
    lv_obj_set_flag(lv_obj_8, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_8, &brightness_80, 0);
    lv_obj_bind_style(lv_obj_8, &brightness_10, 0, &brightness, 10);
    lv_obj_bind_style(lv_obj_8, &brightness_20, 0, &brightness, 20);
    lv_obj_bind_style(lv_obj_8, &brightness_30, 0, &brightness, 30);
    lv_obj_bind_style(lv_obj_8, &brightness_40, 0, &brightness, 40);
    lv_obj_bind_style(lv_obj_8, &brightness_50, 0, &brightness, 50);
    lv_obj_bind_style(lv_obj_8, &brightness_60, 0, &brightness, 60);
    lv_obj_bind_style(lv_obj_8, &brightness_70, 0, &brightness, 70);
    lv_obj_bind_style(lv_obj_8, &brightness_90, 0, &brightness, 90);
    lv_obj_bind_style(lv_obj_8, &brightness_100, 0, &brightness, 100);

    LV_TRACE_OBJ_CREATE("finished");

    return lv_obj_0;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

