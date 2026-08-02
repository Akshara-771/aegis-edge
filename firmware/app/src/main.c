#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include "fault.h"
#include "sensor.h"

int main(void)
{
    printk("\n");
    printk("=====================================\n");
    printk("        AEGIS EDGE STARTED\n");
    printk("=====================================\n");
    fault_set(FAULT_OVERHEAT);
    while (1) {

        int temperature = sensor_get_temperature();
        int voltage = sensor_get_voltage();
        int rpm = sensor_get_rpm();

        printk("Temperature : %d.%d C\n",
               temperature / 10,
               temperature % 10);

        printk("Voltage     : %d.%02d V\n",
               voltage / 100,
               voltage % 100);

        printk("RPM         : %d\n", rpm);

        printk("------------------------------\n");

        k_sleep(K_SECONDS(2));
    }

    return 0;
}
