#include <rte_byteorder.h>

#include "xxhash32.h"

#define xxh_rotl32(x, r) ((x << r) | (x >> (32 - r)))

static inline uint32_t xxhash32_round(const uint32_t input, uint32_t seed) {
    seed += input * PRIME32_2;
    seed = xxh_rotl32(seed, 13);
    seed *= PRIME32_1;
    return seed;
}

/*******************************************************************************
* Description: xxhash32函数，返回hash后的值
* Parameters：
*   @key：要hash的key，这里是IPv4的5元组（或四元组）
*   @length：key的长度，这里是IPv4的5元组（或四元组）的长度
*   @init_val：hash的初始值
* Return: hash后的值
* 参考：https://github.com/Nefelim4ag/jhash_vs_xxhash/blob/master/xxhash.c
********************************************************************************/
uint32_t xxhash32(const void *key, uint32_t length, uint32_t init_val) {
    const uint8_t *pos = (const uint8_t *)key;
    const uint8_t *end = pos + length;
    uint32_t hash;

    if (length >= 16) {
        const uint8_t *const limit = end - 16;
        uint32_t v1 = init_val + PRIME32_1 + PRIME32_2;
        uint32_t v2 = init_val + PRIME32_2;
        uint32_t v3 = init_val + 0;
        uint32_t v4 = init_val - PRIME32_1;

        do {
            v1 = xxhash32_round(*(const uint32_t *)pos, v1);
            pos += 4;
            v2 = xxhash32_round(*(const uint32_t *)pos, v2);
            pos += 4;
            v3 = xxhash32_round(*(const uint32_t *)pos, v3);
            pos += 4;
            v4 = xxhash32_round(*(const uint32_t *)pos, v4);
            pos += 4;
        } while (pos <= limit);

        hash = xxh_rotl32(v1, 1) + xxh_rotl32(v2, 7) + xxh_rotl32(v3, 12) + xxh_rotl32(v4, 18);
    } else {
        hash = init_val + PRIME32_5;
    }

    hash += length;

    while (pos + 4 <= end) {
        hash += *(const uint32_t *)pos * PRIME32_3;
        hash = xxh_rotl32(hash, 17) * PRIME32_4;
        pos += 4;
    }

    while (pos < end) {
        hash += (*pos) * PRIME32_5;
        hash = xxh_rotl32(hash, 11) * PRIME32_1;
        pos++;
    }

    hash ^= hash >> 15;
    hash *= PRIME32_2;
    hash ^= hash >> 13;
    hash *= PRIME32_3;
    hash ^= hash >> 16;

    return hash;
}