# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 14:11:14 2022

@author: Administrator
"""
# from django.conf import settings
import ipdb
import os, time
import socket
import pymysql
import datetime
from py2neo import Node, Relationship, Graph, NodeMatcher


def int2ip(digit):
    result = []
    for i in range(4):
        digit, mod = divmod(digit, 256)
        result.insert(0,mod)
    return '.'.join(map(str,result))

def ip_info(ip):
    qqwry_path = os.path.join(os.path.abspath(__file__), "qqwry.ipdb")

    ip_db = ipdb.City(qqwry_path)
    info = ip_db.find_map(ip, "CN")
    return info["country_name"], info["region_name"], info["city_name"], info["isp_domain"]

def Node_is_Create(graph, label, name):
    matcher = NodeMatcher(graph)
    if matcher.match(label, name = name).first() != None:
        return matcher.match(label, name = name).first()
    else:
        if label == "IP":
            country, region, city, isp_domain = ip_info(name)
            cypher_ = f"CREATE (:IP {{name: '{name}', country: '{country}', region: '{region}', city:'{city}', isp_domain:'{isp_domain}'}})"
            graph.run(cypher_)
            return matcher.match(label, name = name).first()
        else:
            node = Node(label, name = name)
            graph.create(node)
            return node

def Node_is_Create_(graph, label, name, value):
    matcher = NodeMatcher(graph)
    if matcher.match(label, name = name, value = value).first() != None:
        return matcher.match(label, name = name, value = value).first()
    else:
        node = Node(label, name = name, value = value)
        graph.create(node)
        return node

def Relationship_is_Exist(graph, start_node, end_node, relationship):
    if len(list(graph.match(start_node = start_node, end_node = end_node, rel_type=relationship))) > 0:
        return 1
    return -1

def Time_Transformer(timeStamp):
    dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    return otherStyleTime # "2013-10-10 23:40:00"

def Protocol_Transformer(i):
    table = {num:name[8:] for name,num in vars(socket).items() if name.startswith("IPPROTO")}
    return table[i]

import os
def run():
    print("{} 开始...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    try:
        # 打开数据库连接
        db = pymysql.connect(host=os.environ['MYSQL_HOST'],
                            user=os.environ['MYSQL_USER'],
                            password=os.environ['MYSQL_PASSWORD'],
                            database=os.environ['MYSQL_DATABASE'])

        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        counter = 0
        batch_size = 1000
        loop = True
        
        graph = Graph(os.environ['NEO4J_SERVER'], auth=(os.environ['NEO4J_USER'],os.environ['NEO4J_PASSWORD']), name=os.environ['NEO4J_DATABASE'])
        graph.delete_all()

        while loop:
            start = time.time()
            #sql = "SELECT * FROM FlowTables LIMIT " + str(counter) + "," +  str(batch_size)
            #sql = "SELECT * FROM FlowTables WHERE sip IN ( SELECT ip FROM detect_ipimage ) OR \
            #                                     dip IN ( SELECT ip FROM detect_ipimage) \
            #                                     LIMIT " + str(counter) + "," +  str(batch_size)
            sql = "SELECT * FROM FlowTables JOIN detect_ipimage ON \
                    FlowTables.sip = detect_ipimage.ip OR FlowTables.dip = detect_ipimage.ip LIMIT " + str(counter) + "," +  str(batch_size)
            cursor.execute(sql)
            results = cursor.fetchall()
            print('{} [info]: sql查询完毕,用时{:.2f} s'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), time.time()-start), flush=True)

            start = time.time()
            for row in results:
                sip = int2ip(row[1])
                dip = int2ip(row[2])
                session = sip + " to " + dip
                sport = row[3]
                dport = row[4]
                protocol = row[5]
                src_ip = Node_is_Create(graph, "IP", name = sip)
                dst_ip = Node_is_Create(graph, "IP", name = dip)

                relationship = Relationship(src_ip, "to", dst_ip)
                graph.create(relationship)
                flow = Node("Session", name = session, value = Time_Transformer(row[0]))
                graph.create(flow)
                relationship_flow_start = Relationship(src_ip, "To", flow)
                graph.create(relationship_flow_start)
                relationship_flow_end = Relationship(flow, "To", dst_ip)
                graph.create(relationship_flow_end)
                src_port = Node_is_Create(graph, "Sport", name = sport)
                dst_port = Node_is_Create(graph, "Dport", name = dport)
                protocol_ = Node_is_Create_(graph, "Protocol", name = Protocol_Transformer(protocol), value = protocol)
                relationship_sport = Relationship(flow, "sport", src_port)
                graph.create(relationship_sport)
                relationship_dport = Relationship(flow, "dport", dst_port)
                graph.create(relationship_dport)
                relationship_protocol = Relationship(flow, "protocol", protocol_)
                graph.create(relationship_protocol)
                # if row[9] != None:
                #     label_S = Node_is_Create(graph, "Label_Service", name = row[9])
                #     relationship_label_S = Relationship(flow, "service", label_S)
                #     graph.create(relationship_label_S)
                # if row[10] != None:
                #     label_A = Node_is_Create(graph, "Label_Anomaly", name = row[10])
                #     relationship_label_A = Relationship(flow, "Anomaly", label_A)
                #     graph.create(relationship_label_A)
            size = len(results)
            if size < batch_size:
                loop = False
            counter = counter + size
        db.close()
        graph.run('''
        MATCH p=(a)-[:to]-()
        CALL {
            WITH a
            MATCH (a)--()
            WITH a, 10*(log10(count(*)+1)+1)+rand() AS allNeighboursCount
            SET a.allNeighboursCount = allNeighboursCount
        }
        ''')
        print('{} [info]: 成功更新画像，用时{:.2f} s'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), time.time()-start), flush=True)
    except Exception as e:
        print("{} [Error]: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), e), flush=True)
    finally:
        print("{} 结束...".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)

if __name__ == '__main__':
    run()
