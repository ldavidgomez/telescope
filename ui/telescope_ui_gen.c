/**
 * @file telescope_ui_gen.c
 */

/*********************
 *      INCLUDES
 *********************/

#include "telescope_ui_gen.h"

#if LV_USE_XML
#endif /* LV_USE_XML */

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/

/**********************
 *  STATIC VARIABLES
 **********************/

/*----------------
 * Translations
 *----------------*/

/**********************
 *  GLOBAL VARIABLES
 **********************/

/*--------------------
 *  Permanent screens
 *-------------------*/

lv_obj_t * guidance = NULL;

/*----------------
 * Global styles
 *----------------*/

lv_style_t screen_night;
lv_style_t screen_day;
lv_style_t panel_night;
lv_style_t panel_day;
lv_style_t muted_night;
lv_style_t muted_day;
lv_style_t accent_night;
lv_style_t accent_day;
lv_style_t button_night;
lv_style_t button_day;

/*----------------
 * Fonts
 *----------------*/

lv_font_t * font_body;
extern lv_font_t font_body_data;
lv_font_t * font_heading;
extern lv_font_t font_heading_data;
lv_font_t * font_value;
extern lv_font_t font_value_data;
lv_font_t * font_arrow;
extern lv_font_t font_arrow_data;

/*----------------
 * Images
 *----------------*/

/*----------------
 * Subjects
 *----------------*/

lv_subject_t night_mode;
lv_subject_t brightness;
lv_subject_t target_name;
lv_subject_t current_az;
lv_subject_t current_alt;
lv_subject_t target_az;
lv_subject_t target_alt;
lv_subject_t az_direction;
lv_subject_t alt_direction;
lv_subject_t az_error;
lv_subject_t alt_error;
lv_subject_t guide_status;
lv_subject_t connection_status;

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void telescope_ui_init_gen(const char * asset_path)
{
    char buf[256];

    /*----------------
     * Global styles
     *----------------*/

    static bool style_inited = false;

    if (!style_inited) {
        lv_style_init(&screen_night);
        lv_style_set_bg_color(&screen_night, NIGHT_BG);
        lv_style_set_bg_opa(&screen_night, (255 * 100 / 100));
        lv_style_set_text_color(&screen_night, NIGHT_TEXT);
        lv_style_set_text_font(&screen_night, font_body);
        lv_style_set_pad_all(&screen_night, 0);

        lv_style_init(&screen_day);
        lv_style_set_bg_color(&screen_day, DAY_BG);
        lv_style_set_bg_opa(&screen_day, (255 * 100 / 100));
        lv_style_set_text_color(&screen_day, DAY_TEXT);
        lv_style_set_text_font(&screen_day, font_body);
        lv_style_set_pad_all(&screen_day, 0);

        lv_style_init(&panel_night);
        lv_style_set_bg_color(&panel_night, NIGHT_PANEL);
        lv_style_set_bg_opa(&panel_night, (255 * 100 / 100));
        lv_style_set_border_color(&panel_night, NIGHT_BORDER);
        lv_style_set_border_width(&panel_night, 1);
        lv_style_set_radius(&panel_night, 10);
        lv_style_set_pad_all(&panel_night, 10);

        lv_style_init(&panel_day);
        lv_style_set_bg_color(&panel_day, DAY_PANEL);
        lv_style_set_bg_opa(&panel_day, (255 * 100 / 100));
        lv_style_set_border_color(&panel_day, DAY_BORDER);
        lv_style_set_border_width(&panel_day, 1);
        lv_style_set_radius(&panel_day, 10);
        lv_style_set_pad_all(&panel_day, 10);

        lv_style_init(&muted_night);
        lv_style_set_text_color(&muted_night, NIGHT_MUTED);

        lv_style_init(&muted_day);
        lv_style_set_text_color(&muted_day, DAY_MUTED);

        lv_style_init(&accent_night);
        lv_style_set_text_color(&accent_night, NIGHT_ACCENT);

        lv_style_init(&accent_day);
        lv_style_set_text_color(&accent_day, DAY_ACCENT);

        lv_style_init(&button_night);
        lv_style_set_bg_color(&button_night, NIGHT_PANEL);
        lv_style_set_bg_opa(&button_night, (255 * 100 / 100));
        lv_style_set_border_color(&button_night, NIGHT_BORDER);
        lv_style_set_border_width(&button_night, 1);
        lv_style_set_radius(&button_night, 8);
        lv_style_set_text_color(&button_night, NIGHT_TEXT);

        lv_style_init(&button_day);
        lv_style_set_bg_color(&button_day, DAY_PANEL);
        lv_style_set_bg_opa(&button_day, (255 * 100 / 100));
        lv_style_set_border_color(&button_day, DAY_BORDER);
        lv_style_set_border_width(&button_day, 1);
        lv_style_set_radius(&button_day, 8);
        lv_style_set_text_color(&button_day, DAY_TEXT);

        style_inited = true;
    }

    /*----------------
     * Fonts
     *----------------*/

    /* get font 'font_body' from a C array */
    font_body = &font_body_data;
    /* get font 'font_heading' from a C array */
    font_heading = &font_heading_data;
    /* get font 'font_value' from a C array */
    font_value = &font_value_data;
    /* get font 'font_arrow' from a C array */
    font_arrow = &font_arrow_data;


    /*----------------
     * Images
     *----------------*/
    /*----------------
     * Subjects
     *----------------*/
    lv_subject_init_int(&night_mode, 1);
    lv_subject_set_min_value_int(&night_mode, 0);
    lv_subject_set_max_value_int(&night_mode, 1);
    lv_subject_init_int(&brightness, 35);
    lv_subject_set_min_value_int(&brightness, 5);
    lv_subject_set_max_value_int(&brightness, 100);
    static char target_name_buf[UI_SUBJECT_STRING_LENGTH];
    static char target_name_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&target_name,
                           target_name_buf,
                           target_name_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "ALDEBARAN"
                          );
    static char current_az_buf[UI_SUBJECT_STRING_LENGTH];
    static char current_az_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&current_az,
                           current_az_buf,
                           current_az_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "052.0"
                          );
    static char current_alt_buf[UI_SUBJECT_STRING_LENGTH];
    static char current_alt_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&current_alt,
                           current_alt_buf,
                           current_alt_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "+18.0"
                          );
    static char target_az_buf[UI_SUBJECT_STRING_LENGTH];
    static char target_az_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&target_az,
                           target_az_buf,
                           target_az_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "067.4"
                          );
    static char target_alt_buf[UI_SUBJECT_STRING_LENGTH];
    static char target_alt_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&target_alt,
                           target_alt_buf,
                           target_alt_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "+31.8"
                          );
    static char az_direction_buf[UI_SUBJECT_STRING_LENGTH];
    static char az_direction_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&az_direction,
                           az_direction_buf,
                           az_direction_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           ">"
                          );
    static char alt_direction_buf[UI_SUBJECT_STRING_LENGTH];
    static char alt_direction_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&alt_direction,
                           alt_direction_buf,
                           alt_direction_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "^"
                          );
    static char az_error_buf[UI_SUBJECT_STRING_LENGTH];
    static char az_error_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&az_error,
                           az_error_buf,
                           az_error_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "+15.4 deg"
                          );
    static char alt_error_buf[UI_SUBJECT_STRING_LENGTH];
    static char alt_error_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&alt_error,
                           alt_error_buf,
                           alt_error_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "+13.8 deg"
                          );
    static char guide_status_buf[UI_SUBJECT_STRING_LENGTH];
    static char guide_status_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&guide_status,
                           guide_status_buf,
                           guide_status_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "GUIDING"
                          );
    static char connection_status_buf[UI_SUBJECT_STRING_LENGTH];
    static char connection_status_prev_buf[UI_SUBJECT_STRING_LENGTH];
    lv_subject_init_string(&connection_status,
                           connection_status_buf,
                           connection_status_prev_buf,
                           UI_SUBJECT_STRING_LENGTH,
                           "STELLARIUM  OK   IMU  OK   PI  OK"
                          );

    /*----------------
     * Translations
     *----------------*/

#if LV_USE_XML
    /* Register widgets */

    /* Register fonts */
    lv_xml_register_font(NULL, "font_body", font_body);
    lv_xml_register_font(NULL, "font_heading", font_heading);
    lv_xml_register_font(NULL, "font_value", font_value);
    lv_xml_register_font(NULL, "font_arrow", font_arrow);

    /* Register subjects */
    lv_xml_register_subject(NULL, "night_mode", &night_mode);
    lv_xml_register_subject(NULL, "brightness", &brightness);
    lv_xml_register_subject(NULL, "target_name", &target_name);
    lv_xml_register_subject(NULL, "current_az", &current_az);
    lv_xml_register_subject(NULL, "current_alt", &current_alt);
    lv_xml_register_subject(NULL, "target_az", &target_az);
    lv_xml_register_subject(NULL, "target_alt", &target_alt);
    lv_xml_register_subject(NULL, "az_direction", &az_direction);
    lv_xml_register_subject(NULL, "alt_direction", &alt_direction);
    lv_xml_register_subject(NULL, "az_error", &az_error);
    lv_xml_register_subject(NULL, "alt_error", &alt_error);
    lv_xml_register_subject(NULL, "guide_status", &guide_status);
    lv_xml_register_subject(NULL, "connection_status", &connection_status);

    /* Register callbacks */
#endif

    /* Register all the global assets so that they won't be created again when globals.xml is parsed.
     * While running in the editor skip this step to update the preview when the XML changes */
#if LV_USE_XML && !defined(LV_EDITOR_PREVIEW)
    /* Register images */
#endif

#if LV_USE_XML == 0
    /*--------------------
     *  Permanent screens
     *-------------------*/
    /* If XML is enabled it's assumed that the permanent screens are created
     * manaully from XML using lv_xml_create() */
    /* To allow screens to reference each other, create them all before calling the sceen create functions */
    guidance = lv_obj_create(NULL);

    guidance_create();
#endif
}

/* Callbacks */

/**********************
 *   STATIC FUNCTIONS
 **********************/