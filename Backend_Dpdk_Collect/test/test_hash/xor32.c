#include "xor32.h"

uint32_t xor32_hash(const void *key, uint32_t length, uint32_t init_val) {
    const uint32_t *pos = (const uint32_t *)key;
    const uint32_t *end = pos + (length / 4);

    uint32_t result = init_val;

    while (pos != end) {
        result ^= *pos++;
    }

    const uint8_t *pos2 = (const uint8_t*)pos;

    switch (length & 3) {
        case 3:
            result ^= (uint32_t)pos2[2] << 16;
        case 2:
            result ^= (uint32_t)pos2[1] << 8;
        case 1:
            result ^= (uint32_t)pos2[0];
        case 0:
            break;
    }

    return result;
}