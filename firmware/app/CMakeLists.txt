cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

project(aegis_edge)

target_sources(app PRIVATE
    src/main.c
    src/sensor.c
    src/fault.c
    src/fault_detector.c
    src/telemetry.c
    src/config.c
    src/model_data.c
    src/ml_inference.cc
)

target_include_directories(app PRIVATE
    include
)
