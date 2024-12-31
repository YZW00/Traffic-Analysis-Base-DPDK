#include "super_fast_hash.h"

#define get16bits(d) ((((uint32_t)(((const uint8_t *)(d))[1])) << 8)\
                       +(uint32_t)(((const uint8_t *)(d))[0]) )

uint32_t super_fast_hash(const void *key, uint32_t length, uint32_t initval) {
    uint32_t hash = length;
    uint32_t tmp;
    int rem;
    const uint8_t *pos = (const uint8_t *)key;

    rem = length & 3;
    length >>= 2;

    /* Main loop */
    for (;length > 0; length--) {
        hash  += get16bits (pos);
        tmp    = (get16bits (pos+2) << 11) ^ hash;
        hash   = (hash << 16) ^ tmp;
        pos  += 2*sizeof (uint16_t);
        hash  += hash >> 11;
    }

    /* Handle end cases */
    switch (rem) {
        case 3: hash += get16bits (pos);
                hash ^= hash << 16;
                hash ^= pos[sizeof (uint16_t)] << 18;
                hash += hash >> 11;
                break;
        case 2: hash += get16bits (pos);
                hash ^= hash << 11;
                hash += hash >> 17;
                break;
        case 1: hash += *pos;
                hash ^= hash << 10;
                hash += hash >> 1;
    }

    /* Force "avalanching" of final 127 bits */
    hash ^= hash << 3;
    hash += hash >> 5;
    hash ^= hash << 4;
    hash += hash >> 17;
    hash ^= hash << 25;
    hash += hash >> 6;

    return hash;
}