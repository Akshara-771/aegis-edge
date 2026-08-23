#include "sensor.h"
#include "fault.h"

static int temperature = 248;
static int voltage = 330;
static int rpm = 1500;

void sensor_read(sensor_data_t *data)
{
    if (fault_get() == FAULT_OVERHEAT)
    {
        data->temperature = 950;
    }
    else
    {
        temperature++;

        if (temperature > 320)
        {
            temperature = 248;
        }

        data->temperature = temperature;
    }

    if (fault_get() == FAULT_LOW_VOLTAGE)
    {
        data->voltage = 220;
    }
    else
    {
        data->voltage = voltage;
    }

    if (fault_get() == FAULT_HIGH_RPM)
    {
        data->rpm = 4500;
    }
    else
    {
        data->rpm = rpm;
    }
}
