#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

int main(void)
{
    printk("\n");
    printk("=====================================\n");
    printk("        AEGIS EDGE STARTED\n");
    printk("=====================================\n");

    while (1) {
        printk("System Alive\n");
        k_sleep(K_SECONDS(2));
    }

    return 0;
}
