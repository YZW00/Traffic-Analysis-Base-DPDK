#include <stdio.h>
#include <time.h>

#include <rte_common.h>
#include <rte_ethdev.h>
#include <rte_ether.h>
#include <rte_tcp.h>

#include "read_pcap.h"

int read_pcap(const char* file_path, struct IPv4FlowTuple* ipv4_pkts) {
    // struct pcap_header *pcap_file_header = NULL;            // pcap文件头
    struct pcap_packet_header *packet_header = NULL;        // 数据报包头

    // struct rte_ether_hdr *ether_hdr = NULL;                 // 以太网头
    // struct rte_vlan_hdr *vlan_hdr = NULL;                   // vlan头
    struct rte_ipv4_hdr *ipv4_hdr = NULL;                   // ipv4头
    struct rte_tcp_hdr *tcp_hdr = NULL;                     // tcp头
    struct rte_udp_hdr *udp_hdr = NULL;                     // udp头

    struct IPv4FlowTuple ipv4_flow_tuple;                   // 流五元组

    uint32_t ipv4_pkt_count = 0;
    // char my_time[STRSIZE];

    // 初始化，分配内存
    packet_header = (struct pcap_packet_header *)malloc(sizeof(struct pcap_packet_header));
    ipv4_hdr = (struct rte_ipv4_hdr *)malloc(sizeof(struct rte_ipv4_hdr));
    tcp_hdr = (struct rte_tcp_hdr *)malloc(sizeof(struct rte_tcp_hdr));
    udp_hdr = (struct rte_udp_hdr *)malloc(sizeof(struct rte_udp_hdr));
    
    // 打开文件
    FILE *fp = fopen(file_path, "rb");
    if (fp == NULL) {
        fprintf(stderr, "open file failed\n");
        exit(-1);
    }

    uint32_t pkt_offset = 24;                               // pcap文件头偏移量

    // 开始读数据包
    while(fseek(fp, pkt_offset, SEEK_SET) == 0) {
        // 读取数据包头
        memset(packet_header, 0, sizeof(struct pcap_packet_header));        // 以0填充packet_header
        if (fread(packet_header, 16, 1, fp) != 1) {                         // 从fp流里读取1个16个字节大小的元素到packet_header里, 成功读取会返回读取的元素个数
            printf("read packet header failed\n");
            break;
        }

        // // 读取pcap包时间戳，并转换为标准时间格式
        // struct tm *time_info;
        // time_t t = (time_t)packet_header->timestamp;
        // time_info = localtime(&t);
        // strftime(my_time, sizeof(my_time), "%Y-%m-%d %H:%M:%S", time_info);

        // 跳过14个字节的以太网头 + 4字节的VLAN头
        fseek(fp, 18, SEEK_CUR);                                            

        // 读取IP头
        memset(ipv4_hdr, 0, sizeof(struct rte_ipv4_hdr));
        if (fread(ipv4_hdr, 20, 1, fp) != 1) {
            printf("read ipv4 header failed\n");
            break;
        }

        ipv4_flow_tuple.src_ip = ipv4_hdr->src_addr;
        ipv4_flow_tuple.dst_ip = ipv4_hdr->dst_addr;
        ipv4_flow_tuple.proto_id = ipv4_hdr->next_proto_id;

        if (ipv4_flow_tuple.proto_id == IPPROTO_TCP) {
            // 读取TCP头
            memset(tcp_hdr, 0, sizeof(struct rte_tcp_hdr));
            if (fread(tcp_hdr, 20, 1, fp) != 1) {                      
                printf("read tcp header failed\n");
                break;
            }

            ipv4_flow_tuple.src_port = rte_be_to_cpu_16(tcp_hdr->src_port);
            ipv4_flow_tuple.dst_port = rte_be_to_cpu_16(tcp_hdr->dst_port);

            // ipv4flow_print(&ipv4_flow_tuple);

            if (ipv4_pkt_count < MAX_PKT_COUNT) {
                ipv4_pkts[ipv4_pkt_count] = ipv4_flow_tuple;
                ipv4_pkt_count++;
            } else {
                printf("ipv4 packet count is too large\n");
                break;
            }
        } else if (ipv4_flow_tuple.proto_id == IPPROTO_UDP) {
            // 读取UDP头
            memset(udp_hdr, 0, sizeof(struct rte_udp_hdr));
            if (fread(udp_hdr, 8, 1, fp) != 1) {
                printf("read udp header failed\n");
                break;
            }

            ipv4_flow_tuple.src_port = rte_be_to_cpu_16(udp_hdr->src_port);
            ipv4_flow_tuple.dst_port = rte_be_to_cpu_16(udp_hdr->dst_port);

            // ipv4flow_print(&ipv4_flow_tuple);

            if (ipv4_pkt_count < MAX_PKT_COUNT) {
                ipv4_pkts[ipv4_pkt_count] = ipv4_flow_tuple;
                ipv4_pkt_count++;
            } else {
                printf("ipv4 packet count is too large\n");
                break;
            }
        } 

        // 下一个数据包的偏移量
        pkt_offset += 16 + packet_header->packet_length;

    }

    fclose(fp);

    free(packet_header);
    free(ipv4_hdr);
    free(tcp_hdr);
    free(udp_hdr);

    return ipv4_pkt_count;
}