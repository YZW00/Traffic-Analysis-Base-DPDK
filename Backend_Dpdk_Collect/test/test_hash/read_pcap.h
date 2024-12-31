#ifndef READ_PCAP_H
#define READ_PCAP_H

#include "../../src/pcap.h"
#include "../../src/flow_extractor.h"

// #define BUFSIZE 10240
// #define STRSIZE 1024
#define MAX_PKT_COUNT 1024 * 1024 * 2

int read_pcap(const char* file_path, struct IPv4FlowTuple* ipv4_pkts);

#endif