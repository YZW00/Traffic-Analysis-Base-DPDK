#include <stdint.h>
#include <stdbool.h>
#include <signal.h>
#include <argp.h>
#include <inttypes.h>
#include <arpa/inet.h>

#include <mysql/mysql.h>

#include <rte_common.h>
#include <rte_log.h>
#include <rte_memcpy.h>
#include <rte_ethdev.h>
#include <rte_errno.h>
#include <rte_string_fns.h>
#include <rte_version.h>

#include "pcap.h"
#include "core_write.h"
#include "core_capture.h"
#include "statistics.h"
#include "mysql_op.h"

#define STR1(x) #x
#define STR(x) STR1(x)

#define RX_DESC_DEFAULT 512

#define NUM_MBUFS_DEFAULT 8192
#define MBUF_CACHE_SIZE 256

#define MAX_LCORES 1000

#define DPDKCAP_OUTPUT_TEMPLATE_TOKEN_FILECOUNT "\%FCOUNT"
#define DPDKCAP_OUTPUT_TEMPLATE_TOKEN_CORE_ID "\%COREID"
#define DPDKCAP_OUTPUT_TEMPLATE_DEFAULT "output_" DPDKCAP_OUTPUT_TEMPLATE_TOKEN_CORE_ID

#define DPDKCAP_OUTPUT_TEMPLATE_LENGTH 2 * DPDKCAP_OUTPUT_FILENAME_LENGTH

#define RTE_LOGTYPE_DPDKCAP RTE_LOGTYPE_USER1

/* ARGP */
char global_output_file_name[DPDKCAP_OUTPUT_FILENAME_LENGTH] = {0};
const char *argp_program_version = "dpdkcap 1.1";
const char *argp_program_bug_address = "w.b.devries@utwente.nl";
static char doc[] = "A DPDK-based packet capture tool";
static char args_doc[] = "";
static struct argp_option options[] = {
    {"output", 'o', "FILE", 0, "Output FILE template (don't add the "
                               "extension). Use \"" DPDKCAP_OUTPUT_TEMPLATE_TOKEN_CORE_ID "\" for "
                               "inserting the lcore id into the file name (automatically added if not "
                               "used). (default: " DPDKCAP_OUTPUT_TEMPLATE_DEFAULT ")",
     0},
    {"statistics", 'S', 0, 0, "Print statistics every few seconds.", 0},
    {"num-mbuf", 'm', "NB_MBUF", 0, "Total number of memory buffer used to "
                                    "store the packets. Optimal values, in terms of memory usage, are powers "
                                    "of 2 minus 1 (2^q-1) (default: " STR(NUM_MBUFS_DEFAULT) ")",
     0},
    {"per_port_c_cores", 'c', "NB_CORES_PER_PORT", 0, "Number of cores per "
                                                      "port used for capture (default: 1)",
     0},
    {"num_w_cores", 'w', "NB_CORES", 0, "Total number of cores used for "
                                        "writing (default: 1).",
     0},
    {"rx_desc", 'd', "RX_DESC_MATRIX", 0, "This option can be used to "
                                          "override the default number of RX descriptors configured for all queues "
                                          "of each port (" STR(RX_DESC_DEFAULT) "). RX_DESC_MATRIX can have "
                                                                                "multiple formats:\n"
                                                                                "- A single positive value, which will simply replace the default "
                                                                                " number of RX descriptors,\n"
                                                                                "- A list of key-values, assigning a configured number of RX "
                                                                                "descriptors to the given port(s). Format: \n"
                                                                                "  <matrix>   := <key>.<nb_rx_desc> { \",\" <key>.<nb_rx_desc> \",\" "
                                                                                "...\n"
                                                                                "  <key>      := { <interval> | <port> }\n"
                                                                                "  <interval> := <lower_port> \"-\" <upper_port>\n"
                                                                                "  Examples: \n"
                                                                                "  512               - all ports have 512 RX desc per queue\n"
                                                                                "  0.256, 1.512      - port 0 has 256 RX desc per queue,\n"
                                                                                "                      port 1 has 512 RX desc per queue\n"
                                                                                "  0-2.256, 3.1024   - ports 0, 1 and 2 have 256 RX desc per "
                                                                                " queue,\n"
                                                                                "                      port 3 has 1024 RX desc per queue.",
     0},
    {"rotate_seconds", 'G', "T", 0, "Create a new set of files every T "
                                    "seconds. Use strftime formats within the output file template to rename "
                                    "each file accordingly.",
     0},
    {"limit_file_size", 'C', "SIZE", 0, "Before writing a packet, check "
                                        "whether the target file excess SIZE bytes. If so, creates a new file. "
                                        "Use \"" DPDKCAP_OUTPUT_TEMPLATE_TOKEN_FILECOUNT "\" within the output "
                                        "file template to index each new file.",
     0},
    {"portmask", 'p', "PORTMASK", 0, "Ethernet ports mask (default: 0x1).", 0},
    {"snaplen", 's', "LENGTH", 0, "Snap the capture to snaplen bytes "
                                  "(default: 65535).",
     0},
    {"logs", 700, "FILE", 0, "Writes the logs into FILE instead of "
                             "stderr.",
     0},
    {"ip", 'I', "IP", 0, "IP address (default: all ips)", 0},
    {"port", 'P', "Port", 0, "Port (default: all ports)", 0},
    {"timeout", 'T', "Timeout", 0, "Timeout in seconds (default: 10)", 10},
    {"compression", 701, 0, 0, "Compress capture files.", 0},
    {"protocol", 702, "Protocol", 0, "Capture only packets of the given protocol. (default: all protocols)", 0},
    {"send", 703, "Send", 0, "定时将统计信息发送给服务器", 0},
    {"help", 'h', 0, 0, "Print this help and exit.", 0},
    {0}};

struct arguments
{
    char *args[2];
    char output_file_template[DPDKCAP_OUTPUT_FILENAME_LENGTH];
    uint64_t portmask;
    int statistics;
    unsigned long nb_mbufs;
    char *num_rx_desc_str_matrix;
    unsigned long per_port_c_cores;
    unsigned long num_w_cores;
    int compression;
    unsigned long snaplen;
    unsigned long rotate_seconds;
    uint64_t file_size_limit;
    char *log_file;
    rte_be32_t ip;
    rte_be32_t ip_lowerborder;
    rte_be32_t ip_upperborder;
    rte_be16_t port;
    uint16_t ports[MAX_PORTS]; // 端口号数组
    int num_ports; // 实际存储的端口号数量
    uint8_t protocol;
    uint16_t protocols[MAX_PROTOCOLS];
    int num_protocols;
    uint32_t timeout; // 程序运行时间，单位是s
    uint32_t send;    // 定时将统计信息发送给服务器
};

static int parse_matrix_opt(char *arg, unsigned long *matrix,
                            unsigned long max_len)
{
    char *comma_tokens[100];
    int nb_comma_tokens;
    char *dot_tokens[3];
    int nb_dot_tokens;
    char *dash_tokens[3];
    int nb_dash_tokens;

    char *end;

    unsigned long left_key;
    unsigned long right_key;
    unsigned long value;

    nb_comma_tokens = rte_strsplit(arg, strlen(arg), comma_tokens, 100, ',');
    // Case with a single value
    if (nb_comma_tokens == 1 && strchr(arg, '.') == NULL)
    {
        errno = 0;
        value = strtoul(arg, &end, 10);
        if (errno || *end != '\0')
            return -EINVAL;
        for (unsigned long key = 0; key < max_len; key++)
        {
            matrix[key] = value;
        }
        return 0;
    }

    // Key-value matrix
    if (nb_comma_tokens > 0)
    {
        for (int comma = 0; comma < nb_comma_tokens; comma++)
        {
            // Split between left and right side of the dot
            nb_dot_tokens = rte_strsplit(comma_tokens[comma],
                                         strlen(comma_tokens[comma]), dot_tokens, 3, '.');
            if (nb_dot_tokens != 2)
                return -EINVAL;

            // Handle value
            errno = 0;
            value = strtoul(dot_tokens[1], &end, 10);
            if (errno || *end != '\0')
                return -EINVAL;

            // Handle key
            nb_dash_tokens = rte_strsplit(dot_tokens[0],
                                          strlen(dot_tokens[0]), dash_tokens, 3, '-');
            if (nb_dash_tokens == 1)
            {
                // Single value
                left_key = strtoul(dash_tokens[0], &end, 10);
                if (errno || *end != '\0')
                    return -EINVAL;
                right_key = left_key;
            }
            else if (nb_dash_tokens == 2)
            {
                // Interval value
                left_key = strtoul(dash_tokens[0], &end, 10);
                if (errno || *end != '\0')
                    return -EINVAL;
                right_key = strtoul(dash_tokens[1], &end, 10);
                if (errno || *end != '\0')
                    return -EINVAL;
            }
            else
            {
                return -EINVAL;
            }

            // Fill-in the matrix
            if (right_key < max_len && right_key >= left_key)
            {
                for (unsigned long key = left_key; key <= right_key; key++)
                {
                    matrix[key] = value;
                }
            }
            else
            {
                return -EINVAL;
            }
        }
    }
    else
    {
        return -EINVAL;
    }
    return 0;
}

static error_t parse_opt(int key, char *arg, struct argp_state *state)
{
    struct arguments *arguments = state->input;
    char *end;

    struct sockaddr_in sockaddr;
    int ret;

    errno = 0;
    end = NULL;
    switch (key)
    {
    case 'p':
        /* parse hexadecimal string */
        arguments->portmask = strtoul(arg, &end, 16);
        if (arguments->portmask == 0)
        {
            RTE_LOG(ERR, DPDKCAP, "Invalid portmask '%s', no port used\n", arg);
            return -EINVAL;
        }
        break;
    case 'o':
        strncpy(arguments->output_file_template, arg,
                DPDKCAP_OUTPUT_FILENAME_LENGTH);
        break;
    case 'S':
        arguments->statistics = 1;
        break;
    case 'm':
        arguments->nb_mbufs = strtoul(arg, &end, 10);
        break;
    case 'd':
        arguments->num_rx_desc_str_matrix = arg;
        break;
    case 'c':
        arguments->per_port_c_cores = strtoul(arg, &end, 10);
        break;
    case 'w':
        arguments->num_w_cores = strtoul(arg, &end, 10);
        break;
    case 's':
        arguments->snaplen = strtoul(arg, &end, 10);
        break;
    case 'G':
        arguments->rotate_seconds = strtoul(arg, &end, 10);
        break;
    case 'C':
        arguments->file_size_limit = strtoll(arg, &end, 10);
        break;
    case 'I':
        if (strcmp(arg, "0") == 0)
        {
            arguments->ip = 0;
            break;
        }
        else
        {
            bzero(&sockaddr, sizeof(sockaddr));
            ret = inet_pton(AF_INET, arg, &sockaddr.sin_addr);
            if (ret != 1)
            {
                int len = strlen(arg);
                int slash_count = 0;
                int slash_pos = -1;
                for (int i = 0; i < len; i++)
                {
                    if (arg[i] == '/')
                    {
                        slash_count++;
                        if (slash_count > 1)
                            break;
                        slash_pos = i;
                    }
                }
                if (slash_count == 1)
                {
                    char ip_part[slash_pos + 1];
                    char num_part[len - slash_pos];
                    strncpy(ip_part, arg, slash_pos);
                    ip_part[slash_pos] = '\0';
                    strcpy(num_part, arg + slash_pos + 1);
                    ret = inet_pton(AF_INET, ip_part, &sockaddr.sin_addr);
                    if (ret == 1)
                    {
                        char *endptr;
                        long subnet = strtol(num_part, &endptr, 10);
                        if (subnet < 1 || subnet > 32 || *endptr != '\0')
                        {
                            fprintf(stderr, "inet_pton error: %s is not a valid subnet number\n", num_part);
                            return ARGP_ERR_UNKNOWN;
                        }
                        // arguments->ip = htonl(sockaddr.sin_addr.s_addr);
                        uint32_t mask = (0xFFFFFFFFu << subnet) & 0xFFFFFFFFu;
                        arguments->ip_lowerborder = htonl(sockaddr.sin_addr.s_addr) & mask;
                        arguments->ip_upperborder = htonl(sockaddr.sin_addr.s_addr) | (~mask);
                        printf("Lower Border: %d.%d.%d.%d\n", (arguments->ip_lowerborder >> 24) & 0xFF, (arguments->ip_lowerborder >> 16) & 0xFF, (arguments->ip_lowerborder >> 8) & 0xFF, arguments->ip_lowerborder & 0xFF);
                        printf("Upper Border: %d.%d.%d.%d\n", (arguments->ip_upperborder >> 24) & 0xFF, (arguments->ip_upperborder >> 16) & 0xFF, (arguments->ip_upperborder >> 8) & 0xFF, arguments->ip_upperborder & 0xFF);
                        break;
                    }
                }
                if (ret == 0)
                {
                    fprintf(stderr, "inet_pton error: %s is not a valid ip text\n", arg);
                }
                else if (ret == -1)
                {
                    perror("inet_pton error");
                }
                fprintf(stderr, "inet_pton error: unkown error");
                return ARGP_ERR_UNKNOWN;
            }
            arguments->ip = htonl(sockaddr.sin_addr.s_addr);
            break;
        }
    
    case 'P':
    {
        char *token;
        char *saveptr;
        uint16_t ports[MAX_PORTS]; // 定义一个足够大的数组来存储端口号
        int num_ports = 0; // 记录实际存储的端口号数量
        
        // 使用 strtok_r 函数按逗号分割输入字符串
        token = strtok_r(arg, ",", &saveptr);
        while (token != NULL) {
            // 将分割后的子字符串转换为端口号
            errno = 0; // 清除 errno 的值
            char *endptr;
            uint16_t port = strtoul(token, &endptr, 10);
            
            // 检查是否发生了转换错误
            if (errno || (*endptr != '\0' && *endptr != ',')) {
                break;
            }

            // 存储端口号到数组中
            if (port != 0)
                ports[num_ports++] = port;
            
            // 继续处理下一个子字符串
            token = strtok_r(NULL, ",", &saveptr);
        }
        if (errno || (end != NULL && *end != '\0')) break;
        // 将解析得到的端口号数组存储到 arguments 结构体中
        memcpy(arguments->ports, ports, num_ports * sizeof(uint16_t));
        arguments->num_ports = num_ports;
        break;
    }
    case 'T':
        arguments->timeout = strtoul(arg, &end, 10);
    case 700:
        arguments->log_file = arg;
        break;
    case 701:
        arguments->compression = 1;
        break;
    case 702:
    {
        char *token_pro;
        char *saveptr_pro;
        uint16_t protocols[MAX_PROTOCOLS];
        int num_protocols = 0;
        
        token_pro = strtok_r(arg, ",", &saveptr_pro);
        while (token_pro != NULL) {
            errno = 0;
            char *endptr_pro;
            uint16_t protocol = strtoul(token_pro, &endptr_pro, 10);

            if (errno || (*endptr_pro != '\0' && *endptr_pro != ',')) {
                break;
            }
            if (protocol != 0)
                protocols[num_protocols++] = protocol;

            token_pro = strtok_r(NULL, ",", &saveptr_pro);
        }
        if (errno || (end != NULL && *end != '\0')) break;
        memcpy(arguments->protocols, protocols, num_protocols * sizeof(uint16_t));
        arguments->num_protocols = num_protocols;
        break;
    }
    
    case 703:
        arguments->send = strtoul(arg, &end, 10);
        break;
    default:
        return ARGP_ERR_UNKNOWN;
    }
    if (errno || (end != NULL && *end != '\0'))
    {
        RTE_LOG(ERR, DPDKCAP, "Invalid value '%s'\n", arg);
        return -EINVAL;
    }
    return 0;
}
static struct argp argp = {options, parse_opt, args_doc, doc, 0, 0, 0};
/* END OF ARGP */

static struct rte_ring *write_ring;

struct arguments arguments;

static unsigned int portlist[64];
static unsigned int nb_ports;

static struct core_write_stats *cores_stats_write_list;
static struct core_capture_stats *cores_stats_capture_list;

static const struct rte_eth_conf port_conf_default = {
    .rxmode = {
        .mq_mode = RTE_ETH_MQ_RX_NONE,
        .max_lro_pkt_size = RTE_ETHER_MAX_LEN,
    }};

/*
 * Initializes a given port using global settings and with the RX buffers
 * coming from the mbuf_pool passed as a parameter.
 */
static int port_init(
    uint8_t port,
    const uint16_t rx_rings,
    unsigned int num_rxdesc,
    struct rte_mempool *mbuf_pool)
{

    struct rte_eth_conf port_conf = port_conf_default;
    struct rte_eth_dev_info dev_info;
    int retval;
    uint16_t q;
    uint16_t dev_count;

    /* Check if the port id is valid */
#if RTE_VERSION >= RTE_VERSION_NUM(18, 11, 3, 16)
    dev_count = rte_eth_dev_count_avail() - 1;
#else
    dev_count = rte_eth_dev_count() - 1;
#endif

    if (rte_eth_dev_is_valid_port(port) == 0)
    {
        RTE_LOG(ERR, DPDKCAP, "Port identifier %d out of range (0 to %d) or not"
                              " attached.\n",
                port, dev_count);
        return -EINVAL;
    }

    /* Get the device info */
    rte_eth_dev_info_get(port, &dev_info);

    /* Check if the requested number of queue is valid */
    if (rx_rings > dev_info.max_rx_queues)
    {
        RTE_LOG(ERR, DPDKCAP, "Port %d can only handle up to %d queues (%d "
                              "requested).\n",
                port, dev_info.max_rx_queues, rx_rings);
        return -EINVAL;
    }

    /* Check if the number of requested RX descriptors is valid */
    if (num_rxdesc > dev_info.rx_desc_lim.nb_max ||
        num_rxdesc < dev_info.rx_desc_lim.nb_min ||
        num_rxdesc % dev_info.rx_desc_lim.nb_align != 0)
    {
        RTE_LOG(ERR, DPDKCAP, "Port %d cannot be configured with %d RX "
                              "descriptors per queue (min:%d, max:%d, align:%d)\n",
                port, num_rxdesc, dev_info.rx_desc_lim.nb_min,
                dev_info.rx_desc_lim.nb_max, dev_info.rx_desc_lim.nb_align);
        return -EINVAL;
    }

    /* Configure multiqueue (Activate Receive Side Scaling on UDP/TCP fields) */
    if (rx_rings > 1)
    {
        port_conf.rxmode.mq_mode = RTE_ETH_MQ_RX_RSS;
        port_conf.rx_adv_conf.rss_conf.rss_key = NULL;
        port_conf.rx_adv_conf.rss_conf.rss_hf = RTE_ETH_RSS_PROTO_MASK;
    }

    /* Configure the Ethernet device. */
    retval = rte_eth_dev_configure(port, rx_rings, 0, &port_conf);
    if (retval)
    {
        RTE_LOG(ERR, DPDKCAP, "rte_eth_dev_configure(...): %s\n",
                rte_strerror(-retval));
        return retval;
    }

    /* Allocate and set up RX queues. */
    for (q = 0; q < rx_rings; q++)
    {
        // struct rte_eth_rxconf rx_conf;
        // rx_conf.offloads = 0;
        // rx_conf.rx_seg = NULL;
        // rx_conf.rx_nseg = 0;
        rte_eth_rx_queue_setup(port, q, num_rxdesc,
                               rte_eth_dev_socket_id(port), NULL, mbuf_pool);
        if (retval)
        {
            RTE_LOG(ERR, DPDKCAP, "rte_eth_rx_queue_setup(...): %s\n",
                    rte_strerror(-retval));
            return retval;
        }
    }

    /* Stats bindings (if more than one queue) */
    if (dev_info.max_rx_queues > 1)
    {
        for (q = 0; q < rx_rings; q++)
        {
            retval = rte_eth_dev_set_rx_queue_stats_mapping(port, q, q);
            // printf("rx_rings: %d, max_rx_queues: %d, port: %d, queue_id: %d, stat_id: %d\n", rx_rings, dev_info.max_rx_queues, port, q, q);
            if (retval)
            {
                RTE_LOG(WARNING, DPDKCAP, "rte_eth_dev_set_rx_queue_stats_mapping(...):"
                                          " %s\n",
                        rte_strerror(-retval));
                RTE_LOG(WARNING, DPDKCAP, "The queues statistics mapping failed. The "
                                          "displayed queue statistics are thus unreliable.\n");
            }
        }
    }

    /* Enable RX in promiscuous mode for the Ethernet device. */
    retval = rte_eth_promiscuous_enable(port);
    if (retval)
    {
        RTE_LOG(ERR, DPDKCAP, "rte_eth_promiscuous_enable(...): %s\n",
                rte_strerror(-retval));
        return retval;
    }

    /* Display the port MAC address. */
    struct rte_ether_addr addr;
    rte_eth_macaddr_get(port, &addr);
    RTE_LOG(INFO, DPDKCAP, "Port %u: MAC=%02" PRIx8 ":%02" PRIx8 ":%02" PRIx8 ":%02" PRIx8 ":%02" PRIx8 ":%02" PRIx8 ", RXdesc/queue=%d\n",
            (unsigned)port,
            addr.addr_bytes[0], addr.addr_bytes[1], addr.addr_bytes[2],
            addr.addr_bytes[3], addr.addr_bytes[4], addr.addr_bytes[5],
            num_rxdesc);

    return 0;
}

/*
 * Handles signals
 */
volatile bool should_stop = false;
void signal_handler(int sig)
{
    RTE_LOG(NOTICE, DPDKCAP, "Caught signal %s on core %u%s\n",
            strsignal(sig), rte_lcore_id(),
            rte_get_main_lcore() == rte_lcore_id() ? " (MASTER CORE)" : "");
    should_stop = true;
}

/*
 * The main function, which does initialization and calls the per-lcore
 * functions.
 */
int main(int argc, char *argv[])
{
    signal(SIGINT, signal_handler);
    struct core_capture_config *cores_config_capture_list;
    struct core_write_config *cores_config_write_list;
    unsigned int lcoreid_list[MAX_LCORES];
    unsigned int nb_lcores;
    struct rte_mempool *mbuf_pool;
    unsigned int port_id;
    unsigned int i, j;
    unsigned int required_cores;
    unsigned int core_index;
    int result;
    uint16_t dev_count;
    FILE *log_file;
    struct rte_flow_error error;

    /* Initialize the Environment Abstraction Layer (EAL). */
    int ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");

    argc -= ret;
    argv += ret;

    /* Parse arguments */
    arguments = (struct arguments){
        .statistics = 0,
        .nb_mbufs = NUM_MBUFS_DEFAULT,
        .num_rx_desc_str_matrix = NULL,
        .per_port_c_cores = 1,
        .num_w_cores = 1,
        .compression = 0,
        .snaplen = PCAP_SNAPLEN_DEFAULT,
        .portmask = 0x1,
        .rotate_seconds = 0,
        .file_size_limit = 0,
        .log_file = NULL,
        .ip = 0,
        .ip_upperborder = 0,
        .ip_lowerborder = 0,
        .port = 0,
        .num_ports = 0,
        .num_protocols = 0,
        .protocol = 0,
        .timeout = 10,
        .send = 0,
    };
    strncpy(arguments.output_file_template, DPDKCAP_OUTPUT_TEMPLATE_DEFAULT, DPDKCAP_OUTPUT_FILENAME_LENGTH);
    argp_parse(&argp, argc, argv, 0, 0, &arguments);

    printf("IP: %u, port: %d, protocol: %d, timeout: %d\n", arguments.ip, arguments.port, arguments.protocol, arguments.timeout);

    /* Set log level */
#if RTE_VERSION >= RTE_VERSION_NUM(17, 5, 0, 16)
    rte_log_set_level(RTE_LOG_DEBUG, RTE_LOG_DEBUG);
#else
    rte_set_log_type(RTE_LOGTYPE_DPDKCAP, 1);
    rte_set_log_level(RTE_LOG_DEBUG);
#endif

    /* Change log stream if needed */
    if (arguments.log_file)
    {
        log_file = fopen(arguments.log_file, "w");
        if (!log_file)
        {
            rte_exit(EXIT_FAILURE, "Error: Could not open log file: (%d) %s\n",
                     errno, strerror(errno));
        }
        result = rte_openlog_stream(log_file);
        if (result)
        {
            rte_exit(EXIT_FAILURE, "Error: Could not change log stream: (%d) %s\n",
                     errno, strerror(errno));
        }
    }

    // 如果二者相等，说明没有指定-o参数
    if (strcmp(arguments.output_file_template, DPDKCAP_OUTPUT_TEMPLATE_DEFAULT) == 0)
    {
        // 以当前时间作为文件名前缀
        time_t now;
        struct tm *lt;
        time(&now);
        lt = gmtime(&now);
        // sprintf(arguments.output_file_template, "/home/Pcaps/output-%d%02d%02d-%02d%02d%02d", 1900 + lt->tm_year, 1 + lt->tm_mon, lt->tm_mday, 8 + lt->tm_hour, lt->tm_min, lt->tm_sec);
        sprintf(arguments.output_file_template, "./pcaps/output-%d%02d%02d-%02d%02d%02d", 1900 + lt->tm_year, 1 + lt->tm_mon, lt->tm_mday, 8 + lt->tm_hour, lt->tm_min, lt->tm_sec);
        sprintf(global_output_file_name, "./pcaps/output-%d%02d%02d-%02d%02d%02d", 1900 + lt->tm_year, 1 + lt->tm_mon, lt->tm_mday, 8 + lt->tm_hour, lt->tm_min, lt->tm_sec);
    }
    /* Add suffixes to output if needed */
    if (!strstr(arguments.output_file_template, DPDKCAP_OUTPUT_TEMPLATE_TOKEN_CORE_ID))
        strcat(arguments.output_file_template, "_" DPDKCAP_OUTPUT_TEMPLATE_TOKEN_CORE_ID);
    if (arguments.file_size_limit && !strstr(arguments.output_file_template, DPDKCAP_OUTPUT_TEMPLATE_TOKEN_FILECOUNT))
        strcat(arguments.output_file_template, "_" DPDKCAP_OUTPUT_TEMPLATE_TOKEN_FILECOUNT);

    strcat(arguments.output_file_template, ".pcap");

    if (arguments.compression)
        strcat(arguments.output_file_template, ".lzo");

        /* Check if at least one port is available */
#if RTE_VERSION >= RTE_VERSION_NUM(18, 11, 3, 16)
    dev_count = rte_eth_dev_count_avail();
#else
    dev_count = rte_eth_dev_count();
#endif

    if (dev_count == 0)
        rte_exit(EXIT_FAILURE, "Error: No port available.\n");

    /* Fills in the number of rx descriptors matrix */
    unsigned long *num_rx_desc_matrix = calloc(dev_count, sizeof(int));
    if (arguments.num_rx_desc_str_matrix != NULL &&
        parse_matrix_opt(arguments.num_rx_desc_str_matrix,
                         num_rx_desc_matrix, dev_count) < 0)
    {
        rte_exit(EXIT_FAILURE, "Invalid RX descriptors matrix.\n");
    }

    /* Creates the port list */
    nb_ports = 0;
    for (i = 0; i < 64; i++)
    {
        if (!((uint64_t)(1ULL << i) & arguments.portmask))
            continue;
        if (i < dev_count)
            portlist[nb_ports++] = i;
        else
            RTE_LOG(WARNING, DPDKCAP, "Warning: port %d is in portmask, "
                                      "but not enough ports are available. Ignoring...\n",
                    i);
    }
    if (nb_ports == 0)
        rte_exit(EXIT_FAILURE, "Error: Found no usable port. Check portmask "
                               "option.\n");

    RTE_LOG(INFO, DPDKCAP, "Using %u ports to listen on\n", nb_ports);

    /* Checks core number */
    required_cores = (1 + nb_ports * arguments.per_port_c_cores + arguments.num_w_cores);
    if (rte_lcore_count() < required_cores)
    {
        rte_exit(EXIT_FAILURE, "Assign at least %d cores to dpdkcap.\n",
                 required_cores);
    }
    RTE_LOG(INFO, DPDKCAP, "Using %u cores out of %d allocated\n",
            required_cores, rte_lcore_count());

    /* Creates a new mempool in memory to hold the mbufs. */
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", arguments.nb_mbufs,
                                        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());

    if (mbuf_pool == NULL)
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");

    // Initialize buffer for writing to disk
    write_ring = rte_ring_create("Ring for writing",
                                 rte_align32pow2(arguments.nb_mbufs), rte_socket_id(), 0);

    /* Core index */
    core_index = rte_get_next_lcore(-1, 1, 0);

    /* Init stats list */
    cores_stats_write_list =
        malloc(sizeof(struct core_write_stats) * arguments.num_w_cores);
    cores_stats_capture_list =
        malloc(sizeof(struct core_capture_stats) * arguments.per_port_c_cores * nb_ports);

    /* Init config lists */
    cores_config_write_list =
        malloc(sizeof(struct core_write_config) * arguments.num_w_cores);
    cores_config_capture_list =
        malloc(sizeof(struct core_capture_config) * arguments.per_port_c_cores * nb_ports);

    nb_lcores = 0;

    /* 初始化数据库 */
    MYSQL mysql_conn;

    if (collect_mysql(&mysql_conn, MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB) != 0)
    { // 连接数据库
        return -1;
    }

    if (create_table(&mysql_conn, MYSQL_TABLE_NAME) != 0)
    {
        return -1;
    }

    /* Writing cores */
    for (i = 0; i < arguments.num_w_cores; i++)
    {
        // Configure writing core
        struct core_write_config *config = &(cores_config_write_list[i]);
        config->ring = write_ring;
        config->stop_condition = &should_stop;
        config->stats = &(cores_stats_write_list[i]);
        config->output_file_template = arguments.output_file_template;
        config->compression = arguments.compression;
        config->snaplen = arguments.snaplen;
        config->rotate_seconds = arguments.rotate_seconds;
        config->file_size_limit = arguments.file_size_limit;
        config->ip = arguments.ip;
        config->ip_upperborder = arguments.ip_upperborder;
        config->ip_lowerborder = arguments.ip_lowerborder;
        config->port = arguments.port;
        memcpy(config->ports, arguments.ports, arguments.num_ports * sizeof(uint16_t));
        config->num_ports = arguments.num_ports;
        config->protocol = arguments.protocol;
        memcpy(config->protocols, arguments.protocols, arguments.num_protocols * sizeof(uint16_t));
        config->num_protocols = arguments.num_protocols;
        config->mysql_conn = &mysql_conn;

        // Launch writing core
        if (rte_eal_remote_launch((lcore_function_t *)write_core, config, core_index) < 0)
        {
            rte_exit(EXIT_FAILURE, "Could not launch writing process on lcore %d.\n", core_index);
        }

        // Add the core to the list
        lcoreid_list[nb_lcores] = core_index;
        nb_lcores++;

        core_index = rte_get_next_lcore(core_index, SKIP_MAIN, 0);
    }

    /* For each port */
    for (i = 0; i < nb_ports; i++)
    {
        port_id = portlist[i];

        /* Port init */
        int retval = port_init(
            port_id,
            arguments.per_port_c_cores,
            (num_rx_desc_matrix[i] != 0) ? num_rx_desc_matrix[i] : RX_DESC_DEFAULT,
            mbuf_pool);
        if (retval)
        {
            rte_exit(EXIT_FAILURE, "Cannot init port %" PRIu8 "\n", port_id);
        }

        /* Start the port once everything is ready to capture */
        retval = rte_eth_dev_start(port_id);
        if (retval)
        {
            rte_exit(EXIT_FAILURE, "Cannot start port %" PRIu8 "\n", port_id);
        }

        /* Capturing cores */
        for (j = 0; j < arguments.per_port_c_cores; j++)
        {
            // Configure capture core
            struct core_capture_config *config =
                &(cores_config_capture_list[i * arguments.per_port_c_cores + j]);
            config->ring = write_ring;
            config->stop_condition = &should_stop;
            config->stats =
                &(cores_stats_capture_list[i * arguments.per_port_c_cores + j]);
            config->port = port_id;
            config->queue = j;
            // Launch capture core
            if (rte_eal_remote_launch((lcore_function_t *)capture_core,
                                      config, core_index) < 0)
                rte_exit(EXIT_FAILURE, "Could not launch capture process on lcore "
                                       "%d.\n",
                         core_index);

            // Add the core to the list
            lcoreid_list[nb_lcores] = core_index;
            nb_lcores++;

            core_index = rte_get_next_lcore(core_index, SKIP_MAIN, 0);
        }

        // /* Start the port once everything is ready to capture */
        // retval = rte_eth_dev_start(port_id);
        // if (retval) {
        //   rte_exit(EXIT_FAILURE, "Cannot start port %"PRIu8 "\n", port_id);
        // }
    }

    // Initialize statistics timer
    struct stats_data sd = {
        .ring = write_ring,
        .cores_stats_write_list = cores_stats_write_list,
        .cores_write_stats_list_size = arguments.num_w_cores,
        .cores_stats_capture_list = cores_stats_capture_list,
        .cores_capture_stats_list_size = arguments.per_port_c_cores * nb_ports,
        .port_list = portlist,
        .port_list_size = nb_ports,
        .queue_per_port = arguments.per_port_c_cores,
        .log_file = arguments.log_file,
    };

    if (!should_stop)
    {
        if (arguments.statistics && arguments.send == 0)
        {
            signal(SIGINT, SIG_DFL);
            start_stats_display(&sd, arguments.timeout);
            should_stop = true;
        }
        else if (!arguments.statistics && arguments.send != 0)
        {
            signal(SIGINT, SIG_DFL);
            start_stats_send(&sd, arguments.timeout, arguments.send);
            should_stop = true;
        }
        else if (!arguments.statistics && arguments.send == 0)
        {
            signal(SIGINT, SIG_DFL);
            stop_capture_until(&sd, arguments.timeout);
            should_stop = true;
        }
        else
        {
            rte_exit(EXIT_FAILURE, "Invalid combination of arguments.\n");
        }
    }

    // if (arguments.statistics && !should_stop) {
    //   signal(SIGINT, SIG_DFL);
    //   start_stats_display(&sd, arguments.timeout);
    //   should_stop=true;
    // } else if (!arguments.statistics && !should_stop) {
    //   signal(SIGINT, SIG_DFL);
    //   stop_capture_until(&sd, arguments.timeout);
    //   should_stop=true;
    // }

    // Wait for all the cores to complete and exit
    //  RTE_LOG(NOTICE, DPDKCAP, "Waiting for all cores to exit\n");
    //  for(i=0;i<nb_lcores;i++) {
    //    result = rte_eal_wait_lcore(lcoreid_list[i]);
    //    if (result < 0) {
    //      RTE_LOG(ERR, DPDKCAP, "Core %d did not stop correctly.\n",
    //          lcoreid_list[i]);
    //    }
    //  }

    rte_eal_mp_wait_lcore();

    for (int i = 0; i < nb_ports; i++)
    {
        rte_flow_flush(portlist[i], &error);
        ret = rte_eth_dev_stop(portlist[i]);
        if (ret < 0)
        {
            printf("Failed to stop port %u: %s", port_id, rte_strerror(-ret));
        }
        rte_eth_dev_close(portlist[i]);
    }

    if (arguments.send == 0)
    {
        final_stas_display(&sd);
    }
    else
    {
        final_stas_dispaly_and_send(&sd);
    }

    // Finalize
    free(cores_stats_write_list);
    free(cores_stats_capture_list);
    free(cores_config_write_list);
    free(cores_config_capture_list);
    free(num_rx_desc_matrix);

    mysql_close(&mysql_conn); // 关闭连接
    mysql_library_end();      // 关闭MySQL库

    rte_eal_cleanup();

    return 0;
}
