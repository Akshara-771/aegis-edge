#include "config.h"

static const system_config_t system_config =
{
    .max_temperature = 800,
    .min_voltage = 300,
    .max_rpm = 3000
};

const system_config_t *config_get(void)
{
    return &system_config;
}
