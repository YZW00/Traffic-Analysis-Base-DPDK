#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdio.h>
#include <signal.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/shm.h>
#include <unistd.h>

#include <rte_ethdev.h>
#include <rte_timer.h>
#include <rte_ring.h>
#include <rte_log.h>

#include "statistics.h"
#include "utils.h"

#define RTE_LOGTYPE_DPDKCAP RTE_LOGTYPE_USER1

#define STATS_PERIOD_MS 500
#define ROTATING_CHAR "-\\|/"

#define MYPORT 21345
#define BUFFER_SIZE 1024

int sock_cli = 0;
char sendbuf[BUFFER_SIZE];
int time_sequence = 0;

uint64_t global_total_packets_missed = 0;
uint64_t global_total_packets_droped = 0;

extern char csv_file_name[DPDKCAP_OUTPUT_FILENAME_LENGTH];

/*
 * Prints a set of stats
 */
static int print_stats(
    __attribute__((unused)) struct rte_timer *timer,
    struct stats_data *data)
{
    static unsigned int nb_stat_update = 0;
    static struct rte_eth_stats port_statistics;

    uint64_t total_packets = 0;
    uint64_t total_bytes = 0;
    uint64_t total_compressedbytes = 0;
    uint64_t total_packets_missed = 0;
    uint64_t total_packets_droped = 0;

    unsigned int i, j;

    nb_stat_update++;

    for (i = 0; i < data->cores_write_stats_list_size; i++)
    {
        total_packets += data->cores_stats_write_list[i].packets_written;
        total_bytes += data->cores_stats_write_list[i].bytes;
        total_compressedbytes += data->cores_stats_write_list[i].compressed_bytes;
    }

    printf("\e[1;1H\e[2J");
    printf("=== Packet capture statistics %c ===\n",
           ROTATING_CHAR[nb_stat_update % 4]);

    printf("-- GLOBAL --\n");
    printf("Entries free on ring: %u\n", rte_ring_free_count(data->ring));
    printf("Total packets written: %lu\n", total_packets);
    printf("Total bytes written: %s ", bytes_format(total_bytes));
    printf("compressed to %s\n", bytes_format(total_compressedbytes));
    printf("Compressed/uncompressed size ratio: 1 / %.2f\n",
           total_compressedbytes ? (float)total_bytes / (float)total_compressedbytes : 0.0f);

    printf("-- PER WRITING CORE --\n");
    for (i = 0; i < data->cores_write_stats_list_size; i++)
    {
        printf("Writing core %d: %s ",
               data->cores_stats_write_list[i].core_id,
               data->cores_stats_write_list[i].output_file);
        printf("(%s)\n", bytes_format(
                             data->cores_stats_write_list[i].current_file_compressed_bytes));
    }

    printf("-- PER PORT --\n");
    for (i = 0; i < data->port_list_size; i++)
    {
        rte_eth_stats_get(data->port_list[i], &port_statistics);
        printf("- PORT %d -\n", data->port_list[i]);
        printf("Built-in counters:\n"
               "  RX Successful packets: %lu\n"
               "  RX Successful bytes: %s (avg: %d bytes/pkt)\n"
               "  RX Unsuccessful packets: %lu\n"
               "  RX Missed packets: %lu\n  No MBUF: %lu\n",
               port_statistics.ipackets,
               bytes_format(port_statistics.ibytes),
               port_statistics.ipackets ? (int)((float)port_statistics.ibytes / (float)port_statistics.ipackets) : 0,
               port_statistics.ierrors,
               port_statistics.imissed, port_statistics.rx_nombuf);
        printf("Per queue:\n");
        for (j = 0; j < data->queue_per_port; j++)
        {
            printf("  Queue %d RX: %lu RX-Error: %lu\n", j,
                   port_statistics.q_ipackets[j], port_statistics.q_errors[j]);
        }
        printf("  (%d queues hidden)\n",
               RTE_ETHDEV_QUEUE_STAT_CNTRS - data->queue_per_port);

        total_packets_missed += port_statistics.imissed;
        total_packets_droped += port_statistics.ierrors;
    }

    printf("===================================\n");

    global_total_packets_missed = total_packets_missed;
    global_total_packets_droped = total_packets_droped;

    return 0;
}

// 发送统计信息stats到服务器
static void send_stats(__attribute__((unused)) struct rte_timer *timer, struct stats_data *data)
{
    uint64_t total_packets_captured = 0;
    uint64_t total_packets_droped = 0;
    uint64_t total_packets_missed = 0;
    uint64_t total_packets_written = 0;
    uint64_t total_packets_filtered = 0;
    uint64_t total_bytes_wrritten = 0;
    uint64_t total_compressedbytes_written = 0;

    static struct rte_eth_stats port_statistics;

    unsigned int i;

    for (i = 0; i < data->cores_capture_stats_list_size; i++)
    {
        total_packets_captured += data->cores_stats_capture_list[i].packets;
    }

    for (i = 0; i < data->cores_write_stats_list_size; i++)
    {
        total_packets_written += data->cores_stats_write_list[i].packets_written;
        total_packets_filtered += data->cores_stats_write_list[i].packets_filtered;
        total_bytes_wrritten += data->cores_stats_write_list[i].bytes;
        total_compressedbytes_written += data->cores_stats_write_list[i].compressed_bytes;
    }

    // total_packets_droped = total_packets_captured - total_packets_written - total_packets_filtered;

    for (i = 0; i < data->port_list_size; i++)
    {
        rte_eth_stats_get(data->port_list[i], &port_statistics);
        total_packets_missed += port_statistics.imissed;
        total_packets_droped += port_statistics.ierrors;
    }

    global_total_packets_missed = total_packets_missed;
    global_total_packets_droped = total_packets_droped;

    time_sequence ++;
    extern char global_output_file_name[DPDKCAP_OUTPUT_FILENAME_LENGTH];
    sprintf(sendbuf, "{\"sequence\": %d, \"packets_captured\": %lu, \"packets_missed\": %lu, \"packets_droped\": %lu, \"packets_written\": %lu, \"packets_filtered\": %lu, \"bytes_written\": %lu, \"bytes_compressed\": %lu, \"output_filename\": \"%s\"}\n", 
            time_sequence, total_packets_captured, total_packets_missed, total_packets_droped, total_packets_written,
            total_packets_filtered, total_bytes_wrritten, total_compressedbytes_written, global_output_file_name);

    printf("发送：%s\n", sendbuf);

    send(sock_cli, sendbuf, strlen(sendbuf), 0); // 发送
}

/*
 * Handles signals
 */
// static bool should_stop = false;
// static void signal_handler(int sig) {
//   RTE_LOG(NOTICE, DPDKCAP, "Caught signal %s on core %u%s\n",
//       strsignal(sig), rte_lcore_id(),
//       rte_get_main_lcore()==rte_lcore_id()?" (MASTER CORE)":"");
//   should_stop = true;
// }

static struct rte_timer stats_timer;

void start_stats_display(struct stats_data *data, uint32_t timeout)
{
    extern volatile bool should_stop;
    extern void signal_handler(int sig);

    uint64_t prev_tsc = 0, cur_tsc, diff_tsc;
    uint64_t hz;
    uint64_t timer_resolution_cycles;

    struct timeval start_time;
    struct timeval now_time;
    gettimeofday(&start_time, NULL);

    hz = rte_get_timer_hz();
    timer_resolution_cycles = hz / 10; /* around 100ms */

    signal(SIGINT, signal_handler);
    // Initialize timers
    rte_timer_subsystem_init();
    // Timer launch
    rte_timer_init(&(stats_timer));
    rte_timer_reset(&(stats_timer), hz, PERIODICAL, rte_lcore_id(), (void *)print_stats, data);

    // Wait for ctrl+c
    for (;;)
    {
        gettimeofday(&now_time, NULL);
        if (now_time.tv_sec - start_time.tv_sec > timeout)
        {
            should_stop = true;
        }

        if (unlikely(should_stop))
        {
            break;
        }

        cur_tsc = rte_get_timer_cycles();
        diff_tsc = cur_tsc - prev_tsc;
        if (diff_tsc > timer_resolution_cycles)
        {
            rte_timer_manage();
            prev_tsc = cur_tsc;
        }
    }
    rte_timer_stop(&(stats_timer));
    signal(SIGINT, SIG_DFL);
}

void start_stats_send(struct stats_data *data, uint32_t timeout, uint32_t send)
{
    extern volatile bool should_stop;
    extern void signal_handler(int sig);

    uint64_t prev_tsc = 0, cur_tsc, diff_tsc;
    uint64_t hz;
    uint64_t timer_resolution_cycles;

    // 定义sockfd
    sock_cli = socket(AF_INET, SOCK_STREAM, 0);

    unlink("./client.sock"); // 删除socket文件，避免bind失败

    // 定义sockaddr_in
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(MYPORT);                      ///服务器端口
    servaddr.sin_addr.s_addr = inet_addr("【Your_ip_addr_main】"); ///服务器ip

    // 连接服务器，成功返回0，错误返回-1
    if (connect(sock_cli, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        should_stop = true;
        printf("Connect Error!");
        perror("connect");
        exit(1);
    }

    struct timeval start_time;
    struct timeval now_time;
    gettimeofday(&start_time, NULL);

    hz = rte_get_timer_hz();
    timer_resolution_cycles = hz / 10; /* around 100ms */

    signal(SIGINT, signal_handler);
    // Initialize timers
    rte_timer_subsystem_init();
    // Timer launch
    rte_timer_init(&(stats_timer));
    rte_timer_reset(&(stats_timer), hz * send, PERIODICAL, rte_lcore_id(), (void *)send_stats, data);

    // Wait for ctrl+c
    for (;;)
    {
        gettimeofday(&now_time, NULL);
        if (now_time.tv_sec - start_time.tv_sec > timeout)
        {
            should_stop = true;
        }

        if (unlikely(should_stop))
        {
            break;
        }

        cur_tsc = rte_get_timer_cycles();
        diff_tsc = cur_tsc - prev_tsc;
        if (diff_tsc > timer_resolution_cycles)
        {
            rte_timer_manage();
            prev_tsc = cur_tsc;
        }
    }
    rte_timer_stop(&(stats_timer));
    signal(SIGINT, SIG_DFL);
}

// 计时停止
void stop_capture_until(struct stats_data *data, uint32_t timeout)
{
    extern volatile bool should_stop;
    extern void signal_handler(int sig);

    struct timeval start_time;
    struct timeval now_time;
    gettimeofday(&start_time, NULL);

    signal(SIGINT, signal_handler);

    while (1)
    {
        gettimeofday(&now_time, NULL);
        if (now_time.tv_sec - start_time.tv_sec > timeout)
        {
            should_stop = true;
        }

        if (unlikely(should_stop))
        {
            break;
        }
    }

    signal(SIGINT, SIG_DFL);
}


// 输出最终统计信息
void final_stas_display(struct stats_data *data)
{
    uint64_t total_packets_captured = 0;
    uint64_t total_packets_missed = 0;
    uint64_t total_packets_droped = 0;
    uint64_t total_packets_written = 0;
    uint64_t total_packets_filtered = 0;
    uint64_t total_bytes_wrritten = 0;
    uint64_t total_compressedbytes_written = 0;
    unsigned int i;
    // unsigned int j;
    // static struct rte_eth_stats port_statistics;

    // printf("-- PER PORT --\n");
    // for (i = 0; i < data->port_list_size; i++)
    // {
    //     rte_eth_stats_get(data->port_list[i], &port_statistics);
    //     printf("- PORT %d -\n", data->port_list[i]);
    //     printf("Built-in counters:\n"
    //            "  RX Successful packets: %lu\n"
    //            "  RX Successful bytes: %s (avg: %d bytes/pkt)\n"
    //            "  RX Unsuccessful packets: %lu\n"
    //            "  RX Missed packets: %lu\n  No MBUF: %lu\n",
    //            port_statistics.ipackets,
    //            bytes_format(port_statistics.ibytes),
    //            port_statistics.ipackets ? (int)((float)port_statistics.ibytes / (float)port_statistics.ipackets) : 0,
    //            port_statistics.ierrors,
    //            port_statistics.imissed, port_statistics.rx_nombuf);
    //     printf("Per queue:\n");
    //     for (j = 0; j < data->queue_per_port; j++)
    //     {
    //         printf("  Queue %d RX: %lu RX-Error: %lu\n", j,
    //                port_statistics.q_ipackets[j], port_statistics.q_errors[j]);
    //     }
    //     printf("  (%d queues hidden)\n",
    //            RTE_ETHDEV_QUEUE_STAT_CNTRS - data->queue_per_port);
    // }

    printf("Global===================================\n");

    for (i = 0; i < data->cores_capture_stats_list_size; i++)
    {
        total_packets_captured += data->cores_stats_capture_list[i].packets;
    }

    for (i = 0; i < data->cores_write_stats_list_size; i++)
    {
        total_packets_written += data->cores_stats_write_list[i].packets_written;
        total_packets_filtered += data->cores_stats_write_list[i].packets_filtered;
        total_bytes_wrritten += data->cores_stats_write_list[i].bytes;
        total_compressedbytes_written += data->cores_stats_write_list[i].compressed_bytes;
    }

    total_packets_missed = total_packets_captured - total_packets_written - total_packets_filtered;
    total_packets_missed = global_total_packets_missed > total_packets_missed ? global_total_packets_missed : total_packets_missed;
    total_packets_droped = global_total_packets_droped;

    printf("%lu 个数据包收到,\n"
           "%lu 个数据包Missed,\n"
           "%lu 个数据包Droped,\n"
           "%lu 个数据包写入,\n"
           "%lu 个数据包过滤\n"
           "%lu 字节写入,\n"
           "%lu 字节压缩后\n",
           total_packets_captured, total_packets_missed, total_packets_droped, total_packets_written, total_packets_filtered, total_bytes_wrritten, total_compressedbytes_written);

    printf("===================================\n");
}

// 输出最终统计信息并发送最终的统计信息
void final_stas_dispaly_and_send(struct stats_data *data)
{
    uint64_t total_packets_captured = 0;
    uint64_t total_packets_missed = 0;
    uint64_t total_packets_droped = 0;
    uint64_t total_packets_written = 0;
    uint64_t total_packets_filtered = 0;
    uint64_t total_bytes_wrritten = 0;
    uint64_t total_compressedbytes_written = 0;

    unsigned int i;

    for (i = 0; i < data->cores_capture_stats_list_size; i++)
    {
        total_packets_captured += data->cores_stats_capture_list[i].packets;
        // total_packets_droped += data->cores_stats_capture_list[i].missed_packets;
    }

    for (i = 0; i < data->cores_write_stats_list_size; i++)
    {
        total_packets_written += data->cores_stats_write_list[i].packets_written;
        total_packets_filtered += data->cores_stats_write_list[i].packets_filtered;
        total_bytes_wrritten += data->cores_stats_write_list[i].bytes;
        total_compressedbytes_written += data->cores_stats_write_list[i].compressed_bytes;
    }

    total_packets_missed = total_packets_captured - total_packets_written - total_packets_filtered;
    total_packets_missed = global_total_packets_missed > total_packets_missed ? global_total_packets_missed : total_packets_missed;
    total_packets_droped = global_total_packets_droped;

    printf("Global===================================\n");

    printf("%lu 个数据包收到,\n"
           "%lu 个数据包Missed,\n"
           "%lu 个数据包Droped,\n"
           "%lu 个数据包写入,\n"
           "%lu 个数据包过滤\n"
           "%lu 字节写入,\n"
           "%lu 字节压缩后\n",
           total_packets_captured, total_packets_missed, total_packets_droped, total_packets_written, total_packets_filtered, total_bytes_wrritten, total_compressedbytes_written);

    printf("===================================\n");

    // sprintf(sendbuf, "{\"sequence\": -1, \"packets_captured\": %lu, \"packets_droped\": %lu, \"packets_written\": %lu, \"packets_filtered\": %lu, \"bytes_written\": %lu, \"bytes_compressed\": %lu}",
    //     total_packets_captured, total_packets_droped, total_packets_written,
    //     total_packets_filtered, total_bytes_wrritten, total_compressedbytes_written);

    sprintf(sendbuf, "{\"sequence\": -1, \"packets_captured\": %lu, \"packets_missed\": %lu, \"packets_droped\": %lu, \"packets_written\": %lu, \"packets_filtered\": %lu, \"bytes_written\": %lu, \"bytes_compressed\": %lu}\n", 
        total_packets_captured, total_packets_missed, total_packets_droped, total_packets_written,
        total_packets_filtered, total_bytes_wrritten, total_compressedbytes_written);

    printf("发送最终统计信息：%s\n", sendbuf);
    send(sock_cli, sendbuf, strlen(sendbuf), 0); // 发送

    // 关闭连接
    close(sock_cli);
}