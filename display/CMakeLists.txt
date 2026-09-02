cmake_minimum_required(VERSION 3.20)

project(telescope_display_simulator C)

include(FetchContent)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

find_package(SDL2 REQUIRED)

set(CONFIG_LV_BUILD_DEMOS OFF CACHE BOOL "" FORCE)
set(CONFIG_LV_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(CONFIG_LV_USE_THORVG_INTERNAL OFF CACHE BOOL "" FORCE)
set(LV_BUILD_CONF_DIR ${CMAKE_CURRENT_SOURCE_DIR} CACHE PATH "" FORCE)

FetchContent_Declare(
    lvgl
    GIT_REPOSITORY https://github.com/lvgl/lvgl.git
    GIT_TAG v9.4.0
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(lvgl)

target_include_directories(lvgl PRIVATE ${SDL2_INCLUDE_DIRS})

add_executable(
    telescope-display
    simulator/main.c
    src/telescope_ui.c
)

target_include_directories(
    telescope-display
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${SDL2_INCLUDE_DIRS}
)

target_compile_definitions(
    telescope-display
    PRIVATE
        LV_CONF_INCLUDE_SIMPLE
)

target_link_libraries(
    telescope-display
    PRIVATE
        lvgl
        ${SDL2_LIBRARIES}
        m
)
