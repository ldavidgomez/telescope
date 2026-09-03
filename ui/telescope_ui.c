/**
 * @file telescope_ui.c
 */

/*********************
 *      INCLUDES
 *********************/

#include "telescope_ui.h"

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

#if defined(LV_EDITOR_PREVIEW)
typedef struct {
    const char * current_az;
    const char * current_alt;
    const char * az_error;
    const char * alt_error;
    int32_t sector;
    int32_t stage;
    const char * status;
} preview_sample_t;
#endif

/**********************
 *  STATIC PROTOTYPES
 **********************/

#if defined(LV_EDITOR_PREVIEW)
static void preview_timer_cb(lv_timer_t * timer);
#endif

/**********************
 *  STATIC VARIABLES
 **********************/

#if defined(LV_EDITOR_PREVIEW)
static const preview_sample_t preview_samples[] = {
    {"052.0", "+18.0", "+15.4 deg", "+13.8 deg", 7, 0, "COARSE"},
    {"055.4", "+21.6", "+12.0 deg", "+10.2 deg", 7, 0, "COARSE"},
    {"058.4", "+24.0",  "+9.0 deg",  "+7.8 deg", 7, 0, "COARSE"},
    {"060.2", "+26.2",  "+7.2 deg",  "+5.6 deg", 7, 0, "COARSE"},
    {"062.3", "+28.0",  "+5.1 deg",  "+3.8 deg", 7, 0, "COARSE"},
    {"064.1", "+29.3",  "+3.3 deg",  "+2.5 deg", 7, 0, "COARSE"},
    {"065.4", "+30.6",  "+2.0 deg",  "+1.2 deg", 7, 1, "FINE"},
    {"066.3", "+31.1",  "+1.1 deg",  "+0.7 deg", 7, 1, "FINE"},
    {"066.9", "+31.5",  "+0.5 deg",  "+0.3 deg", 7, 1, "FINE"},
    {"067.2", "+31.9",  "+0.2 deg",  "-0.1 deg", 1, 1, "FINE"},
    {"067.4", "+31.8",  "+0.0 deg",  "+0.0 deg", 7, 2, "ALIGNED"},
    {"067.4", "+31.8",  "+0.0 deg",  "+0.0 deg", 7, 2, "ALIGNED"},
    {"067.4", "+31.8",  "+0.0 deg",  "+0.0 deg", 7, 2, "ALIGNED"},
};

static uint32_t preview_sample_index;
#endif

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

void telescope_ui_init(const char * asset_path)
{
    telescope_ui_init_gen(asset_path);

#if defined(LV_EDITOR_PREVIEW)
    preview_timer_cb(NULL);
    lv_timer_create(preview_timer_cb, 700, NULL);
#endif
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

#if defined(LV_EDITOR_PREVIEW)
static void preview_timer_cb(lv_timer_t * timer)
{
    LV_UNUSED(timer);

    const preview_sample_t * sample = &preview_samples[preview_sample_index];

    lv_subject_copy_string(&current_az, sample->current_az);
    lv_subject_copy_string(&current_alt, sample->current_alt);
    lv_subject_copy_string(&az_error, sample->az_error);
    lv_subject_copy_string(&alt_error, sample->alt_error);
    lv_subject_set_int(&guide_sector, sample->sector);
    lv_subject_set_int(&guide_stage, sample->stage);
    lv_subject_copy_string(&guide_status, sample->status);

    const uint32_t sample_count = sizeof(preview_samples) / sizeof(preview_samples[0]);
    preview_sample_index = (preview_sample_index + 1) % sample_count;
}
#endif
