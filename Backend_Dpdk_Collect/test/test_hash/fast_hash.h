#ifndef FAST_HASH_H
#define FAST_HASH_H

#include <stdint.h>

uint64_t fasthash64(const void *key, uint32_t length, uint64_t init_val);
uint32_t fasthash32(const void *key, uint32_t length, uint32_t init_val);

#endif