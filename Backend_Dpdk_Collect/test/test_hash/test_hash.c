#include <rte_jhash.h>
#include <rte_hash_crc.h>
#include <rte_common.h> 

#include "read_pcap.h"

#include "fast_hash.h"
#include "fnv32.h"
#include "ipsx.h"
#include "lookup3.h"
#include "murmur_hash.h"
#include "one_at_a_time.h"
#include "super_fast_hash.h"
#include "xor32.h"
#include "xxhash32.h"

#define MAX_FLOW_NUM 1024 * 1024

// static uint32_t hash_counts[MAX_FLOW_NUM];

static struct IPv4FlowTuple ipv4_pkts[MAX_PKT_COUNT];
static struct IPv4FlowTuple ipv4_flows[MAX_FLOW_NUM];

const char* hash_funcs[] = {"FastHash", "Fnv32", "Ipsx", "Lookup3", "MurmurHash", "OneAtATime", "RteCrc32", "RteJHash", "SuperFastHash", "Xor32", "XxHash32"};


// 测试单个Hash函数
void test_hash_func(uint32_t (*hash_func)(const void *, uint32_t, uint32_t), size_t hash_func_id, uint32_t key_length, uint32_t init_val, uint32_t pkt_num, const char *log_path) {
    uint32_t hash_value;
    uint64_t start_time;
    uint64_t end_time;
    uint64_t duration;

    uint32_t flow_count = 0;
    uint32_t conflicts = 0;

    FILE *fp = fopen(log_path, "w");

    start_time = rte_rdtsc();

    for (size_t i=0; i<pkt_num; i++) {
        hash_value = hash_func(&ipv4_pkts[i], key_length, init_val);
        hash_value = hash_value &  (MAX_FLOW_NUM - 1);
        
        if (ipv4_flows[hash_value].src_ip == 0) {
            ipv4_flows[hash_value] = ipv4_pkts[i];
            flow_count++;
        } else {
            if (!ipv4_flow_equal(&ipv4_pkts[i], &ipv4_flows[hash_value])) {
                conflicts++;
                // printf("hash冲突: %u\n", hash_value);
                // ipv4flow_print(&ipv4_pkts[i]);
                // ipv4flow_print(&ipv4_flows[hash_value]);
                fprintf(fp, "Hash Value: %u\nFlow Before: %s\nFlow After: %s\n", hash_value, ipv4flow_format_str(&ipv4_flows[hash_value]), ipv4flow_format_str(&ipv4_pkts[i]));
                ipv4_flows[hash_value] = ipv4_pkts[i];
            }
        }
    }

    end_time = rte_rdtsc();
    duration = end_time - start_time; 

    // 清空ipv4_flows
    for (size_t i=0; i<MAX_FLOW_NUM; i++) {
        ipv4_flows[i].src_ip = 0;
    }

    printf("%s: duration: %lu, collisions: %u, pkts: %u, flows: %u\n\n", hash_funcs[hash_func_id], duration, conflicts, pkt_num, flow_count);
}


// 使用随机的五元组测试现有hash函数的速度与冲突率
void test_hash_with_random_flows(uint32_t key_length, uint32_t init_val) {
    /* 生成随机的IPv4 pkt的五元组*/
    for (size_t i=0; i<MAX_PKT_COUNT; i++) {
        ipv4_pkts[i] = (struct IPv4FlowTuple) {
            .src_ip = rand(),
            .dst_ip = rand(),
            .src_port = rand(),
            .dst_port = rand(),
            .proto_id = rand()
        };
    }

    /* 测试现有hash函数的速度与冲突率 */
    test_hash_func(fasthash32, 0, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/fasthash32.txt");
    test_hash_func(ipv4_fnv1_32_hash, 1, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/fnv32.txt");
    test_hash_func(ipv4_ipsx_hash, 2, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/ipsx.txt");
    test_hash_func(lookup3_hash, 3, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/lookup3.txt");
    test_hash_func(murmur3_hash32, 4, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/murmurhash.txt");
    test_hash_func(one_at_a_time_hash, 5, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/one_at_a_time.txt");
    test_hash_func(rte_hash_crc, 6, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/rte_crc32.txt");
    test_hash_func(rte_jhash, 7, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/rte_jhash.txt");
    test_hash_func(super_fast_hash, 8, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/super_fast_hash.txt");
    test_hash_func(xor32_hash, 9, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/xor32.txt");
    test_hash_func(xxhash32, 10, key_length, init_val, MAX_PKT_COUNT, "/home/flow-extractor/test/test_hash/log/random/xxhash32.txt");
}


// 使用pcap文件中的五元组测试现有hash函数的速度与冲突率
void test_hash_with_pcap_flows(const char *pcap_path, uint32_t key_length, uint32_t init_val) {
    /* 从pcap文件中读取IPv4流的五元组*/
    int ipv4_pkt_count = read_pcap(pcap_path, ipv4_pkts);
    printf("共有%u个ipv4数据包\n", ipv4_pkt_count);

    // 初始化ipv4_flows表
    for (int i=0; i< MAX_FLOW_NUM; i++) {
        ipv4_flows[i].src_ip = 0;
        ipv4_flows[i].dst_ip = 0;
        ipv4_flows[i].src_port = 0;
        ipv4_flows[i].dst_port = 0;
        ipv4_flows[i].proto_id = 0;
    }

    /* 测试现有hash函数的速度与冲突率 */
    test_hash_func(fasthash32, 0, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/fasthash32.txt");
    test_hash_func(ipv4_fnv1_32_hash, 1, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/fnv32.txt");
    test_hash_func(ipv4_ipsx_hash, 2, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/ipsx.txt");
    test_hash_func(lookup3_hash, 3, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/lookup3.txt");
    test_hash_func(murmur3_hash32, 4, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/murmurhash.txt");
    test_hash_func(one_at_a_time_hash, 5, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/one_at_a_time.txt");
    test_hash_func(rte_hash_crc, 6, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/rte_crc32.txt");
    test_hash_func(rte_jhash, 7, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/rte_jhash.txt");
    test_hash_func(super_fast_hash, 8, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/super_fast_hash.txt");
    test_hash_func(xor32_hash, 9, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/xor32.txt");
    test_hash_func(xxhash32, 10, key_length, init_val, ipv4_pkt_count, "/home/flow-extractor/test/test_hash/log/pcap/xxhash32.txt");
}

int main() {
    printf("*********************开始使用随机Pkt测试*********************\n");
    test_hash_with_random_flows(12, 0);

    printf("*********************开始使用pcap包中的Pkt测试*********************\n");
    test_hash_with_pcap_flows("/home/flow-extractor/pcaps/output_01_000.pcap", 12, 0);

    return 0;
}

// // 从pcap包中读取MAX_PKT_COUNT个数据包的五元组，然后HASH到容量为MAX_FLOW_NUM的数组中，测试碰撞率
// int main() {
//     // 读取pcap文件
//     int ipv4_pkt_count = read_pcap("/home/flow-extractor/pcaps/output_01_000.pcap", ipv4_pkts);

//     printf("共有%u个ipv4数据包\n", ipv4_pkt_count);

//     // 初始化hash表
//     for (int i=0; i< MAX_FLOW_NUM; i++) {
//         ipv4_flows[i].src_ip = 0;
//         ipv4_flows[i].dst_ip = 0;
//         ipv4_flows[i].src_port = 0;
//         ipv4_flows[i].dst_port = 0;
//         ipv4_flows[i].proto_id = 0;
//     }

//     // 计算hash值
//     uint32_t hash_value = 0;
//     uint32_t flow_count = 0;
//     uint32_t conflicts = 0;

//     // u_int8_t key_length = sizeof(struct IPv4FlowTuple);

//     FILE *fp = fopen("hash_values.txt", "w");

//     for (int i = 0; i < ipv4_pkt_count; i++) {
//         // hash_value = ipv4_ipsx_hash(&ipv4_pkts[i], key_length, MAX_FLOW_NUM);
//         hash_value = ipv4_fnv1_32_hash(&ipv4_pkts[i], 13, MAX_FLOW_NUM);
//         // hash_value = rte_jhash(&ipv4_pkts[i], 13, MAX_FLOW_NUM);
//         // hash_value = rte_hash_crc(&ipv4_pkts[i], key_length, MAX_FLOW_NUM);

//         // hash_value = hash_value % 1048573;
//         // hash_value = hash_value % 2097143;
//         hash_value = hash_value & (MAX_FLOW_NUM - 1);

//         if (ipv4_flows[hash_value].src_ip == 0) {
//             ipv4_flows[hash_value] = ipv4_pkts[i];
//             flow_count++;
//         } else {
//             if (!ipv4_flow_equal(&ipv4_pkts[i], &ipv4_flows[hash_value])) {
//                 conflicts++;
//                 // printf("hash冲突: %u\n", hash_value);
//                 // ipv4flow_print(&ipv4_pkts[i]);
//                 // ipv4flow_print(&ipv4_flows[hash_value]);
//                 fprintf(fp, "Hash Value: %u\nFlow Before: %s\nFlow After: %s\n", hash_value, ipv4flow_format_str(&ipv4_flows[hash_value]), ipv4flow_format_str(&ipv4_pkts[i]));
//                 ipv4_flows[hash_value] = ipv4_pkts[i];
//             }
//         }
//     }

//     printf("在%u个包里，共有%u个流，共有%u次hash冲突\n", ipv4_pkt_count, flow_count, conflicts);

//     fclose(fp);

//     return 0;
// }   

