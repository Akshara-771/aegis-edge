#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include "fault.h"
#include "sensor.h"
#include "fault_detector.h"
#include "telemetry.h"
#include "ml_inference.h"

int main(void)
{
    sensor_data_t sensor;

    int counter = 0;

    printk("\n");
    printk("=====================================\n");
    printk("        AEGIS EDGE STARTED\n");
    printk("=====================================\n");

    telemetry_init();

    if (ml_inference_init() != 0)
    {
        printk("ML initialization FAILED\n");
    }
    else
    {
        printk("ML initialization SUCCESS\n");
    }

    while (1)
    {
        counter++;

        /* OVERHEAT */
        if (counter == 5)
        {
            printk("\n*** OVERHEAT FAULT INJECTED ***\n\n");
            fault_set(FAULT_OVERHEAT);
        }

        /* RECOVER */
        if (counter == 10)
        {
            printk("\n*** SYSTEM RECOVERED ***\n\n");
            fault_set(FAULT_NONE);
        }

        /* LOW VOLTAGE */
        if (counter == 15)
        {
            printk("\n*** LOW VOLTAGE FAULT INJECTED ***\n\n");
            fault_set(FAULT_LOW_VOLTAGE);
        }

        /* RECOVER */
        if (counter == 20)
        {
            printk("\n*** SYSTEM RECOVERED ***\n\n");
            fault_set(FAULT_NONE);
        }

        /* HIGH RPM */
        if (counter == 25)
        {
            printk("\n*** HIGH RPM FAULT INJECTED ***\n\n");
            fault_set(FAULT_HIGH_RPM);
        }

        /* RECOVER and restart test sequence */
        if (counter == 30)
        {
            printk("\n*** SYSTEM RECOVERED ***\n\n");
            fault_set(FAULT_NONE);
            counter = 0;
        }

        sensor_read(&sensor);

        ml_fault_t ml_result = ml_predict(
            sensor.temperature / 10.0f,
            sensor.voltage / 100.0f,
            (float)sensor.rpm
        );

        const char *ml_names[] = {
            "NORMAL",
            "OVERHEAT",
            "LOW_VOLTAGE",
            "HIGH_RPM"
        };

        printk("ML PREDICTION: %s\n", ml_names[ml_result]);

        fault_type_t rule_result = fault_detector_run(&sensor);
        printk("RULE PREDICTION: %s\n",telemetry_fault_name(rule_result));
        telemetry_log(&sensor);

        printk("------------------------------\n");

        k_sleep(K_SECONDS(2));
    }

    return 0;
}
