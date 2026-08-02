#include "sensor.h"
#include "fault.h"

static int temperature = 248;
static int voltage = 330;
static int rpm = 1500;

int sensor_get_temperature(void)
{
    switch (fault_get())
    {
        case FAULT_OVERHEAT:
            return 950;     // 95.0°C

        default:
            temperature++;

            if (temperature > 320)
            {
                temperature = 248;
            }

            return temperature;
    }
}

int sensor_get_voltage(void)
{
    switch (fault_get())
    {
        case FAULT_LOW_VOLTAGE:
            return 220;     // 2.20V

        default:
            return voltage;
    }
}

int sensor_get_rpm(void)
{
    switch (fault_get())
    {
        case FAULT_HIGH_RPM:
            return 4500;

        default:
            return rpm;
    }
}
