#ifndef SENSOR_H
#define SENSOR_H

typedef struct
{
    int temperature;   // x10
    int voltage;       // x100
    int rpm;

} sensor_data_t;

void sensor_read(sensor_data_t *data);

#endif
