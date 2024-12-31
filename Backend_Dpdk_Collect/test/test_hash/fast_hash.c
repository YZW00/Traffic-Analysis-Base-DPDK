#include <fast_hash.h>

/*******************************************************************************
* Description: fast Hash函数，返回hash后的值
* Parameters：
*   @key：要hash的key，这里是IPv4的5元组（或四元组）
*   @length：key的长度，这里是IPv4的5元组（或四元组）的长度
*   @init_val：hash的初始值
* Return: hash后的值
* 参考：https://github.com/ztanml/fast-hash
********************************************************************************/
#define fast_hash_mix(h) ({     \
    h ^= h >> 23;               \
    h *= 0x2127599bf4325c37ULL; \
    h ^= h >> 47;               \
})

uint64_t fasthash64(const void *key, uint32_t length, uint64_t init_val) {
    const uint64_t m = 0x880355f21e6d1965ULL;
    const uint64_t *pos = (const uint64_t *)key;
    const uint64_t *end = pos + (length / 8);
    const uint8_t *pos2;
    uint64_t h = init_val ^ (length * m);
    uint64_t v;

    while (pos != end) {
        v = *pos++;
        h ^= fast_hash_mix(v);
        h *= m;
    }

    pos2 = (const uint8_t*)pos;
    v = 0;

    switch (length & 7) {
        case 7: v ^= (uint64_t)pos2[6] << 48;
        case 6: v ^= (uint64_t)pos2[5] << 40;
        case 5: v ^= (uint64_t)pos2[4] << 32;
        case 4: v ^= (uint64_t)pos2[3] << 24;
        case 3: v ^= (uint64_t)pos2[2] << 16;
        case 2: v ^= (uint64_t)pos2[1] << 8;
        case 1: v ^= (uint64_t)pos2[0];
                h ^= fast_hash_mix(v);
                h *= m;
    };

    return fast_hash_mix(h);
}

uint32_t fasthash32(const void *key, uint32_t length, uint32_t init_val) {
    const uint32_t m = 0x57559429;
    const uint32_t *pos = (const uint32_t *)key;
    const uint32_t *end = pos + (length / 4);

    uint32_t h = init_val ^ (length * m);
    uint32_t v;

    while (pos != end) {
        v = *pos++;
        h ^= fast_hash_mix(v);
        h *= m;
    }

    const uint8_t *pos2 = (const uint8_t*)pos;
    v = 0;

    switch (length & 3) {
        case 3: v ^= (uint32_t)pos2[2] << 16;
        case 2: v ^= (uint32_t)pos2[1] << 8;
        case 1: v ^= (uint32_t)pos2[0];
                h ^= fast_hash_mix(v);
                h *= m;
    };

    return fast_hash_mix(h);
}