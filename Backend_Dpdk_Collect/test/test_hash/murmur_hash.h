#ifndef MURMUR_HASH_H
#define MURMUR_HASH_H

#include <stdint.h>

uint32_t murmur3_hash32(const void *key, uint32_t length, uint32_t initval);

#endif