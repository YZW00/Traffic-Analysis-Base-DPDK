# SPDX-License-Identifier: BSD-3-Clause
# Copyright(c) 2017 Intel Corporation

# meson file, for building this example as part of a main DPDK build.
#
# To build this example as a standalone application with an already-installed
# DPDK instance, use 'make'

project('test_hash', 'C',)

allow_experimental_apis = true
incdir = include_directories('/usr/include')
dpdk = dependency('libdpdk')
sources = files(
        'test_hash.c',
        'ipsx.c',
        'fnv32.c',
        'one_at_a_time.c',
        'lookup3.c',
        'fast_hash.c',
        'murmur_hash.c',
        'super_fast_hash.c',
        'xor32.c',
        'xxhash32.c',
        'read_pcap.c',
        '../../src/flow_extractor.c',
)
executable('test_hash', sources, include_directories : incdir, dependencies: dpdk)