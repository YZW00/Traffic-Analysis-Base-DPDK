#include <stdbool.h>
#include <signal.h>
#include <string.h>

#include <rte_log.h>
#include <rte_lcore.h>
#include <rte_ethdev.h>
#include <rte_version.h>

#include "core_capture.h"

#define RTE_LOGTYPE_DPDKCAP RTE_LOGTYPE_USER1

/*
 * Capture the traffic from the given port/queue tuple
 */
int capture_core(const struct core_capture_config *config)
{
    struct rte_mbuf *bufs[DPDKCAP_CAPTURE_BURST_SIZE];
    uint16_t nb_rx;
    int nb_rx_enqueued;
    int i;

    RTE_LOG(INFO, DPDKCAP, "Core %u is capturing packets for port %u\n",
            rte_lcore_id(), config->port);

    /* Init stats */
    *(config->stats) = (struct core_capture_stats){
        .core_id = rte_lcore_id(),
        .packets = 0,
        .missed_packets = 0,
    };

    /* Run until the application is quit or killed. */
    for (;;)
    {
        /* Stop condition */
        if (unlikely(*(config->stop_condition)))
        {
            // struct rte_eth_stats port_statistics;
            // rte_eth_stats_get(config->port, &port_statistics);
            // printf("- PORT %d -\n", config->port);
            // printf("Built-in counters:\n"
            //     "  RX Successful packets: %lu\n"
            //     "  RX Successful bytes: %lu (avg: %d bytes/pkt)\n"
            //     "  RX Unsuccessful packets: %lu\n"
            //     "  RX Missed packets: %lu\n  No MBUF: %lu\n",
            //     port_statistics.ipackets,
            //     port_statistics.ibytes,
            //     port_statistics.ipackets ? (int)((float)port_statistics.ibytes / (float)port_statistics.ipackets) : 0,
            //     port_statistics.ierrors,
            //     port_statistics.imissed, port_statistics.rx_nombuf);
            // printf("  - Queue %d RX: %lu RX-Error: %lu\n", config->queue, port_statistics.q_ipackets[config->queue], port_statistics.q_errors[config->queue]);
            break;
        }

        /* Retrieve packets and put them into the ring */
        // 如果ring已满，则无法再放入数据，此时会阻塞
        nb_rx = rte_eth_rx_burst(config->port, config->queue, bufs, DPDKCAP_CAPTURE_BURST_SIZE);

        if (likely(nb_rx > 0))
        {
            nb_rx_enqueued = rte_ring_enqueue_burst(config->ring, (void *)bufs, nb_rx, NULL);

            /* Update stats */
            if (nb_rx_enqueued == nb_rx)
            {
                config->stats->packets += nb_rx_enqueued;
            }
            else
            {
                config->stats->missed_packets += (nb_rx - nb_rx_enqueued);
                /* Free whatever we can't put in the write ring */
                for (i = nb_rx_enqueued; i < nb_rx; i++)
                {
                    rte_pktmbuf_free(bufs[i]);
                }
            }
        }
        // else {
        //     /* No packets received, wait a bit */
        //     printf("No packets received, wait a bit\n");
        //     rte_delay_us_block(1);
        // }
    }

    RTE_LOG(INFO, DPDKCAP, "Closed capture core %d (port %d)\n",
            rte_lcore_id(), config->port);

    return 0;
}
