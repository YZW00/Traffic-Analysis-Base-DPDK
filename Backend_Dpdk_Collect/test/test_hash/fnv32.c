#include <fnv32.h>

/*******************************************************************************
* Description: fnv1_32 Hash函数，返回hash后的值
* Parameters：
*   @key：要hash的key，这里是IPv4的5元组（或四元组）
*   @length：key的长度，这里是IPv4的5元组（或四元组）的长度
*   @init_val：hash的初始值，对于32位的fnv1_32函数，初始值应为2166136261
* Return: hash后的值
********************************************************************************/
uint32_t ipv4_fnv1_32_hash(const void *key, uint32_t length, uint32_t init_val) {
    const uint8_t *k = (const uint8_t *)key;

    uint32_t result = FNV32_OFFSET_BASIS;

    for (uint8_t i = 0; i < length; i++) {
        // result += (result<<1) + (result<<4) + (result<<7) + (result<<8) + (result<<24);
        result *= FNV32_PRIME;          // 用*=反而更快
        result ^= (uint32_t) k[i];
    }

    return result;
}


/*******************************************************************************
* Description: fnv1a_32 Hash函数，返回hash后的值
* Parameters：
*   @key：要hash的key，这里是IPv4的5元组（或四元组）
*   @length：key的长度，这里是IPv4的5元组（或四元组）的长度
*   @init_val：hash的初始值，对于32位的fnv1_32函数，初始值应为2166136261
* Return: hash后的值
********************************************************************************/
uint32_t ipv4_fnv1a_32_hash(const void *key, uint32_t length, uint32_t init_val) {
    const uint8_t *k = (const uint8_t *)key;

    uint32_t result = init_val;

    for (uint8_t i = 0; i < length; i++) {
        result ^= (uint32_t) k[i];
        result += (result<<1) + (result<<4) + (result<<7) + (result<<8) + (result<<24); 
    }

    return result;
}