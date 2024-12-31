#ifndef LOOKUP3_H
#define LOOKUP3_H

#include <stdint.h>

uint32_t lookup3_hash(const void *key, uint32_t length, uint32_t initval);

#endif