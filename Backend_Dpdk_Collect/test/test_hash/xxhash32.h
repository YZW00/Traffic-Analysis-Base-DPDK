#ifndef XXHASH32_H
#define XXHASH32_H

#include <stdint.h>

static const uint32_t PRIME32_1 = 2654435761U;
static const uint32_t PRIME32_2 = 2246822519U;
static const uint32_t PRIME32_3 = 3266489917U;
static const uint32_t PRIME32_4 =  668265263U;
static const uint32_t PRIME32_5 =  374761393U;

uint32_t xxhash32(const void *key, uint32_t length, uint32_t init_val);

#endif