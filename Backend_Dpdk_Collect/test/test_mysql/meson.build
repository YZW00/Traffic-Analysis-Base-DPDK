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
mysql = dependency('mysqlclient')
sources = files(
    'src/test_mysql.c',
    'src/generate_query.c',
)
executable('test_mysql', sources, include_directories : incdir, dependencies: [dpdk, mysql])