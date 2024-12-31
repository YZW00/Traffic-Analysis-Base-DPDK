#include <one_at_a_time.h>

/*******************************************************************************
* Description: one at a time Hash函数，返回hash后的值
* Parameters：
*   @key：要hash的key，这里是IPv4的5元组（或四元组）
*   @length：key的长度，这里是IPv4的5元组（或四元组）的长度
*   @init_val：hash的初始值
* Return: hash后的值
* 参考：https://en.wikipedia.org/wiki/Jenkins_hash_function
********************************************************************************/
uint32_t one_at_a_time_hash(const void *key, uint32_t length, uint32_t init_val) {
    const uint8_t *k = (const uint8_t *)key;

    uint32_t i = 0;
    uint32_t hash = init_val;
    
    while (i != length) {
        hash += k[i++];
        hash += hash << 10;
        hash ^= hash >> 6;
    }

    hash += hash << 3;
    hash ^= hash >> 11;
    hash += hash << 15;

    return hash;
}
