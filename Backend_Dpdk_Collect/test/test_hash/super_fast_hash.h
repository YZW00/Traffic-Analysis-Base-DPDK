#ifndef SUPER_FAST_HASH_H_
#define SUPER_FAST_HASH_H_

#include <stdint.h>

uint32_t super_fast_hash(const void *key, uint32_t length, uint32_t initval);

#endif  // SUPER_FAST_HASH_H_
