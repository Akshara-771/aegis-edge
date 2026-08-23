#include <zephyr/sys/printk.h>

#include "fault_detector.h"
#include "config.h"
#include "fault.h"

fault_type_t fault_detector_run(const sensor_data_t *data)
{
    const system_config_t *config = config_get();

    if (data->temperature > config->max_temperature)
    {
        printk("ALERT: OVERHEAT DETECTED!\n");
        return FAULT_OVERHEAT;
    }

    if (data->voltage < config->min_voltage)
    {
        printk("ALERT: LOW VOLTAGE DETECTED!\n");
        return FAULT_LOW_VOLTAGE;
    }

    if (data->rpm > config->max_rpm)
    {
        printk("ALERT: HIGH RPM DETECTED!\n");
        return FAULT_HIGH_RPM;
    }

    return FAULT_NONE;
}
