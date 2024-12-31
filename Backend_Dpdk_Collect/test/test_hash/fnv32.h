#ifndef FNV32_H
#define FNV32_H

#include <stdint.h>

#define FNV32_OFFSET_BASIS 2166136261
#define FNV32_PRIME 16777619

uint32_t ipv4_fnv1_32_hash(const void *key, uint32_t length, uint32_t seed);

#endif
