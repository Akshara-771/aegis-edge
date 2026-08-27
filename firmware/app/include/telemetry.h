#ifndef TELEMETRY_H
#define TELEMETRY_H

#include "sensor.h"
#include "fault.h"
#include "ml_inference.h"

void telemetry_init(void);
void telemetry_log(const sensor_data_t *sensor,
                   ml_fault_t ml_result,
                   fault_type_t rule_result);

const char *telemetry_fault_name(fault_type_t fault);

#endif
