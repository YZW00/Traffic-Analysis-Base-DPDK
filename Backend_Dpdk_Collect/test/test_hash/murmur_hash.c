#include "murmur_hash.h"


uint32_t murmur3_hash32(const void *key, uint32_t length, uint32_t init_val) {
    const uint32_t *pos = (const uint32_t *)key;
    const uint32_t *end = pos + (length / 4);

    uint32_t h1 = init_val;

    const uint32_t c1 = 0xcc9e2d51;
    const uint32_t c2 = 0x1b873593;

    uint32_t k1 = 0;

    while (pos != end) {
        k1 = *pos++;

        k1 *= c1;
        k1 = (k1 << 15) | (k1 >> (32 - 15));
        k1 *= c2;

        h1 ^= k1;
        h1 = (h1 << 13) | (h1 >> (32 - 13));
        h1 = h1 * 5 + 0xe6546b64;
    }

    const uint8_t *tail = (const uint8_t *)pos;

    k1 = 0;

    switch(length & 3) {
        case 3: k1 ^= tail[2] << 16;
        case 2: k1 ^= tail[1] << 8;
        case 1: k1 ^= tail[0];
                k1 *= c1; 
                k1 = (k1 << 15) | (k1 >> (32 - 15)); 
                k1 *= c2; 
                h1 ^= k1;
    };

    h1 ^= length;

    h1 ^= h1 >> 16;
    h1 *= 0x85ebca6b;
    h1 ^= h1 >> 13;
    h1 *= 0xc2b2ae35;
    h1 ^= h1 >> 16;

    return h1;
}