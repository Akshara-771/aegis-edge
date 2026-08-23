#include <zephyr/sys/printk.h>

#include "fault_detector.h"
#include "config.h"

void fault_detector_run(sensor_data_t *data)
{
    const system_config_t *config = config_get();

    if (data->temperature > config->max_temperature)
    {
        printk("ALERT: OVERHEAT DETECTED!\n");
    }

    if (data->voltage < config->min_voltage)
    {
        printk("ALERT: LOW VOLTAGE DETECTED!\n");
    }

    if (data->rpm > config->max_rpm)
    {
        printk("ALERT: HIGH RPM DETECTED!\n");
    }
}
