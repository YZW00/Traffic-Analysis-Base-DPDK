#include <ipsx.h>

/*******************************************************************************
* Description: IPSX Hash函数，返回hash后的值
* Parameters：
*   @key：要hash的key，这里是IPv4的5元组（或四元组）
*   @length：key的长度，这里是IPv4的5元组（或四元组）的长度
*   @init_val：hash的初始值
* Return: hash后的值
********************************************************************************/
uint32_t ipv4_ipsx_hash(const void *key, uint32_t length, uint32_t init_val) {
    const uint32_t *k = (const uint32_t *)key;
    uint32_t src_ip, dst_ip, sd_ports;
    uint32_t tmp1, tmp2;   //中间变量
    uint32_t result =  init_val;

    if (length > 11) {
        src_ip = k[0];   // 源IP地址
        dst_ip = k[1];   // 宿IP地址
        sd_ports = k[2];   // 源端口号 + 宿端口号
    }

    tmp1 = src_ip ^ dst_ip;
    tmp2 = sd_ports;
    result = tmp1 << 8;
    result ^= tmp1 >> 4;
    result ^= tmp1 >> 12;
    result = tmp1 >> 16;
    result ^= tmp2 << 6;
    result ^= tmp2 << 10;
    result ^= tmp2 << 14;
    result ^= tmp2 >> 7;
    
    return result;
}
