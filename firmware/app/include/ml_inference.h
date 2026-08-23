#ifndef ML_INFERENCE_H
#define ML_INFERENCE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    ML_FAULT_NORMAL = 0,
    ML_FAULT_OVERHEAT = 1,
    ML_FAULT_LOW_VOLTAGE = 2,
    ML_FAULT_HIGH_RPM = 3
} ml_fault_t;

int ml_inference_init(void);

ml_fault_t ml_predict(float temperature, float voltage, float rpm);

#ifdef __cplusplus
}
#endif

#endif
