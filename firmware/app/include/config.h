#ifndef CONFIG_H
#define CONFIG_H

typedef struct
{
    int max_temperature;
    int min_voltage;
    int max_rpm;
} system_config_t;

const system_config_t *config_get(void);

#endif
