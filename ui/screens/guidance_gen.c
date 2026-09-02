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
    lv_obj_set_x(lv_label_0, 14);
    lv_obj_set_y(lv_label_0, 8);
    lv_label_bind_text(lv_label_0, &target_name, NULL);
    lv_obj_set_style_text_font(lv_label_0, font_heading, 0);
    
    lv_obj_t * lv_label_1 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_1, 374);
    lv_obj_set_y(lv_label_1, 10);
    lv_label_bind_text(lv_label_1, &guide_status, NULL);
    lv_obj_add_style(lv_label_1, &accent_night, 0);
    lv_obj_bind_style(lv_label_1, &accent_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_obj_1 = lv_obj_create(lv_obj_0);
    lv_obj_set_x(lv_obj_1, 12);
    lv_obj_set_y(lv_obj_1, 40);
    lv_obj_set_width(lv_obj_1, 222);
    lv_obj_set_height(lv_obj_1, 160);
    lv_obj_set_flag(lv_obj_1, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_1, &panel_night, 0);
    lv_obj_bind_style(lv_obj_1, &panel_day, 0, &night_mode, 0);
    lv_obj_t * lv_label_2 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_2, 0);
    lv_obj_set_y(lv_label_2, 0);
    lv_label_set_text(lv_label_2, "CURRENT POSITION");
    lv_obj_add_style(lv_label_2, &muted_night, 0);
    lv_obj_bind_style(lv_label_2, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_3 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_3, 0);
    lv_obj_set_y(lv_label_3, 38);
    lv_label_set_text(lv_label_3, "AZ");
    lv_obj_set_style_text_font(lv_label_3, font_heading, 0);
    
    lv_obj_t * lv_label_4 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_4, 52);
    lv_obj_set_y(lv_label_4, 31);
    lv_label_bind_text(lv_label_4, &current_az, NULL);
    lv_obj_set_style_text_font(lv_label_4, font_value, 0);
    
    lv_obj_t * lv_label_5 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_5, 0);
    lv_obj_set_y(lv_label_5, 99);
    lv_label_set_text(lv_label_5, "ALT");
    lv_obj_set_style_text_font(lv_label_5, font_heading, 0);
    
    lv_obj_t * lv_label_6 = lv_label_create(lv_obj_1);
    lv_obj_set_x(lv_label_6, 52);
    lv_obj_set_y(lv_label_6, 92);
    lv_label_bind_text(lv_label_6, &current_alt, NULL);
    lv_obj_set_style_text_font(lv_label_6, font_value, 0);
    
    lv_obj_t * lv_obj_2 = lv_obj_create(lv_obj_0);
    lv_obj_set_x(lv_obj_2, 246);
    lv_obj_set_y(lv_obj_2, 40);
    lv_obj_set_width(lv_obj_2, 222);
    lv_obj_set_height(lv_obj_2, 160);
    lv_obj_set_flag(lv_obj_2, LV_OBJ_FLAG_SCROLLABLE, false);
    lv_obj_add_style(lv_obj_2, &panel_night, 0);
    lv_obj_bind_style(lv_obj_2, &panel_day, 0, &night_mode, 0);
    lv_obj_t * lv_label_7 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_7, 0);
    lv_obj_set_y(lv_label_7, 0);
    lv_label_set_text(lv_label_7, "MOVE TELESCOPE");
    lv_obj_add_style(lv_label_7, &muted_night, 0);
    lv_obj_bind_style(lv_label_7, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_8 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_8, 2);
    lv_obj_set_y(lv_label_8, 29);
    lv_label_bind_text(lv_label_8, &az_direction, NULL);
    lv_obj_set_style_text_font(lv_label_8, font_arrow, 0);
    lv_obj_add_style(lv_label_8, &accent_night, 0);
    lv_obj_bind_style(lv_label_8, &accent_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_9 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_9, 50);
    lv_obj_set_y(lv_label_9, 32);
    lv_label_set_text(lv_label_9, "AZ");
    lv_obj_set_style_text_font(lv_label_9, font_heading, 0);
    
    lv_obj_t * lv_label_10 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_10, 90);
    lv_obj_set_y(lv_label_10, 27);
    lv_label_bind_text(lv_label_10, &az_error, NULL);
    lv_obj_set_style_text_font(lv_label_10, font_heading, 0);
    
    lv_obj_t * lv_label_11 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_11, 2);
    lv_obj_set_y(lv_label_11, 91);
    lv_label_bind_text(lv_label_11, &alt_direction, NULL);
    lv_obj_set_style_text_font(lv_label_11, font_arrow, 0);
    lv_obj_add_style(lv_label_11, &accent_night, 0);
    lv_obj_bind_style(lv_label_11, &accent_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_12 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_12, 50);
    lv_obj_set_y(lv_label_12, 94);
    lv_label_set_text(lv_label_12, "ALT");
    lv_obj_set_style_text_font(lv_label_12, font_heading, 0);
    
    lv_obj_t * lv_label_13 = lv_label_create(lv_obj_2);
    lv_obj_set_x(lv_label_13, 90);
    lv_obj_set_y(lv_label_13, 89);
    lv_label_bind_text(lv_label_13, &alt_error, NULL);
    lv_obj_set_style_text_font(lv_label_13, font_heading, 0);
    
    lv_obj_t * lv_label_14 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_14, 16);
    lv_obj_set_y(lv_label_14, 211);
    lv_label_set_text(lv_label_14, "TARGET");
    lv_obj_add_style(lv_label_14, &muted_night, 0);
    lv_obj_bind_style(lv_label_14, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_label_15 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_15, 88);
    lv_obj_set_y(lv_label_15, 211);
    lv_label_set_text(lv_label_15, "AZ");
    
    lv_obj_t * lv_label_16 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_16, 112);
    lv_obj_set_y(lv_label_16, 211);
    lv_label_bind_text(lv_label_16, &target_az, NULL);
    
    lv_obj_t * lv_label_17 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_17, 192);
    lv_obj_set_y(lv_label_17, 211);
    lv_label_set_text(lv_label_17, "ALT");
    
    lv_obj_t * lv_label_18 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_18, 226);
    lv_obj_set_y(lv_label_18, 211);
    lv_label_bind_text(lv_label_18, &target_alt, NULL);
    
    lv_obj_t * lv_label_19 = lv_label_create(lv_obj_0);
    lv_obj_set_x(lv_label_19, 16);
    lv_obj_set_y(lv_label_19, 238);
    lv_label_bind_text(lv_label_19, &connection_status, NULL);
    lv_obj_add_style(lv_label_19, &muted_night, 0);
    lv_obj_bind_style(lv_label_19, &muted_day, 0, &night_mode, 0);
    
    lv_obj_t * lv_button_0 = lv_button_create(lv_obj_0);
    lv_obj_set_x(lv_button_0, 12);
    lv_obj_set_y(lv_button_0, 274);
    lv_obj_set_width(lv_button_0, 112);
    lv_obj_set_height(lv_button_0, 36);
    lv_obj_add_style(lv_button_0, &button_night, 0);
    lv_obj_bind_style(lv_button_0, &button_day, 0, &night_mode, 0);
    lv_subject_increment_dsc_t * subject_increment_event_0 = lv_obj_add_subject_increment_event(lv_button_0, &brightness, LV_EVENT_CLICKED, -10);
    lv_obj_set_subject_increment_event_min_value(lv_button_0, subject_increment_event_0, 5);
    lv_obj_set_subject_increment_event_max_value(lv_button_0, subject_increment_event_0, 100);
    lv_obj_t * lv_label_20 = lv_label_create(lv_button_0);
    lv_obj_set_align(lv_label_20, LV_ALIGN_CENTER);
    lv_label_set_text(lv_label_20, "BRIGHT -");
    
    lv_obj_t * lv_button_1 = lv_button_create(lv_obj_0);
    lv_obj_set_x(lv_button_1, 134);
    lv_obj_set_y(lv_button_1, 274);
    lv_obj_set_width(lv_button_1, 212);
    lv_obj_set_height(lv_button_1, 36);
    lv_obj_add_style(lv_button_1, &button_night, 0);
    lv_obj_bind_style(lv_button_1, &button_day, 0, &night_mode, 0);
    lv_subject_increment_dsc_t * subject_increment_event_1 = lv_obj_add_subject_increment_event(lv_button_1, &night_mode, LV_EVENT_CLICKED, 1);
    lv_obj_set_subject_increment_event_min_value(lv_button_1, subject_increment_event_1, 0);
    lv_obj_set_subject_increment_event_max_value(lv_button_1, subject_increment_event_1, 1);
    lv_obj_set_subject_increment_event_rollover(lv_button_1, subject_increment_event_1, true);
    lv_obj_t * lv_label_21 = lv_label_create(lv_button_1);
    lv_obj_set_x(lv_label_21, 16);
    lv_obj_set_align(lv_label_21, LV_ALIGN_LEFT_MID);
    lv_label_set_text(lv_label_21, "DAY / NIGHT");
    
    lv_obj_t * lv_label_22 = lv_label_create(lv_button_1);
    lv_obj_set_x(lv_label_22, 154);
    lv_obj_set_align(lv_label_22, LV_ALIGN_RIGHT_MID);
    lv_label_bind_text(lv_label_22, &brightness, "%d%%");
    
    lv_obj_t * lv_button_2 = lv_button_create(lv_obj_0);
    lv_obj_set_x(lv_button_2, 356);
    lv_obj_set_y(lv_button_2, 274);
    lv_obj_set_width(lv_button_2, 112);
    lv_obj_set_height(lv_button_2, 36);
    lv_obj_add_style(lv_button_2, &button_night, 0);
    lv_obj_bind_style(lv_button_2, &button_day, 0, &night_mode, 0);
    lv_subject_increment_dsc_t * subject_increment_event_2 = lv_obj_add_subject_increment_event(lv_button_2, &brightness, LV_EVENT_CLICKED, 10);
    lv_obj_set_subject_increment_event_min_value(lv_button_2, subject_increment_event_2, 5);
    lv_obj_set_subject_increment_event_max_value(lv_button_2, subject_increment_event_2, 100);
    lv_obj_t * lv_label_23 = lv_label_create(lv_button_2);
    lv_obj_set_align(lv_label_23, LV_ALIGN_CENTER);
    lv_label_set_text(lv_label_23, "BRIGHT +");

    LV_TRACE_OBJ_CREATE("finished");

    return lv_obj_0;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

