#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include "telemetry.h"

const char *telemetry_fault_name(fault_type_t fault)
{
    switch (fault)
    {
    case FAULT_OVERHEAT:
        return "OVERHEAT";

    case FAULT_LOW_VOLTAGE:
        return "LOW_VOLTAGE";

    case FAULT_HIGH_RPM:
        return "HIGH_RPM";

    default:
        return "NONE";
    }
}

void telemetry_init(void)
{
    printk("CSV,timestamp_ms,temperature_c,voltage_v,rpm,fault,ml_prediction,rule_prediction\n");
}

void telemetry_log(const sensor_data_t *sensor,
                   ml_fault_t ml_result,
                   fault_type_t rule_result)
{
    fault_type_t fault = fault_get();
    const char *fault_name = telemetry_fault_name(fault);
    const char *ml_names[] = {
    "NORMAL",
    "OVERHEAT",
    "LOW_VOLTAGE",
    "HIGH_RPM"
};

const char *ml_name = ml_names[ml_result];
const char *rule_name = telemetry_fault_name(rule_result);

    /*
     * Human-readable telemetry
     */
    printk("TIME=%lld ms | ", k_uptime_get());

    printk("TEMP=%d.%d C | ",
           sensor->temperature / 10,
           sensor->temperature % 10);

    printk("VOLT=%d.%02d V | ",
           sensor->voltage / 100,
           sensor->voltage % 100);

    printk("RPM=%d | ", sensor->rpm);

    printk("FAULT=%s\n", fault_name);

    /*
     * Machine-readable CSV telemetry
     */
printk("CSV,%lld,%d.%d,%d.%02d,%d,%s,%s,%s\n",
       k_uptime_get(),
       sensor->temperature / 10,
       sensor->temperature % 10,
       sensor->voltage / 100,
       sensor->voltage % 100,
       sensor->rpm,
       fault_name,
       ml_name,
       rule_name);

}
