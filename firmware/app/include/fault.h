#ifndef FAULT_H
#define FAULT_H

typedef enum
{
    FAULT_NONE = 0,
    FAULT_OVERHEAT,
    FAULT_LOW_VOLTAGE,
    FAULT_HIGH_RPM
} fault_type_t;

void fault_set(fault_type_t fault);

fault_type_t fault_get(void);

#endif
