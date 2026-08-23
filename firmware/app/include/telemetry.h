#ifndef TELEMETRY_H
#define TELEMETRY_H

#include "sensor.h"
#include "fault.h"

void telemetry_init(void);
void telemetry_log(const sensor_data_t *sensor);

const char *telemetry_fault_name(fault_type_t fault);

#endif
