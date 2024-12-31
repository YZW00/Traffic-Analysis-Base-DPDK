#ifndef XOR32_H
#define XOR32_H

#include <stdint.h>

uint32_t xor32_hash(const void *key, uint32_t length, uint32_t init_val);

#endif