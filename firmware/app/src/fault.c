#include "fault.h"

static fault_type_t current_fault = FAULT_NONE;

void fault_set(fault_type_t fault)
{
    current_fault = fault;
}

fault_type_t fault_get(void)
{
    return current_fault;
}
