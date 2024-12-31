#ifndef TEST_MYSQL_H
#define TEST_MYSQL_H

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#include <mysql/mysql.h>

#include "generate_query.h"


#define MYSQL_HOST "127.0.0.1"          // 连接MySQL数据库的主机地址
#define MYSQL_USER "A"              // 连接MySQL数据库的用户名
#define MYSQL_PASS "AA"         // 连接MySQL数据库的密码
#define MYSQL_DB "AAA"     // 连接MySQL数据库的数据库名

#define MAX_PDU_NUM 24                  // PDU最大数量
#define DEFAULT_PDU_NUM 24              // PDU默认数量
#define PDU_NUM 24                      // PDU数量

#define INSERT_BATCH_SIZE 1024 * 2          // MySQL批量插入的数据量

#define MAX_FLOWS_IN_DEVICE 1024 * 1024   // 设备最大流量

#endif
