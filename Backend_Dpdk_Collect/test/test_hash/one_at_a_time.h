#ifndef ONE_AT_A_TIME_H
#define ONE_AT_A_TIME_H

#include <stdint.h>

uint32_t one_at_a_time_hash(const void *key, uint32_t length, uint32_t init_val);

#endif