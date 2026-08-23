#ifndef FAULT_DETECTOR_H
#define FAULT_DETECTOR_H

#include "sensor.h"
#include "fault.h"

fault_type_t fault_detector_run(const sensor_data_t *data);

#endif
