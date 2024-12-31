from django.db import models

# Create your models here.
import os
tshark_path = os.environ["TSHARK_BIN"]

def add_str(str1, str2):
    str1_l = []
    l1 = len(str1) - 1
    while l1 >= 0:
        str1_l.append(int(str1[l1]))
        l1 -= 1
    str2_l = []
    l2 = len(str2) - 1
    while l2 >= 0:
        str2_l.append(int(str2[l2]))
        l2 -= 1
    i = 0
    res = []
    while i < len(str1_l) and i < len(str2_l):
        res.append(str1_l[i] + str2_l[i])
        i += 1
    while i < len(str1_l):
        res.append(str1_l[i])
        i += 1
    while i < len(str2_l):
        res.append(str2_l[i])
        i += 1
    res.append(0)
    i = 0
    co = 0
    while i < len(res):
        res[i] += co
        if res[i] >= 10:
            co = 1
            res[i] %= 10
        else:
            co = 0
        i += 1
    if res[-1] == 0:
        res.pop()
    str_r = []
    i = len(res) - 1
    while i >= 0:
        str_r.append(str(res[i]))
        i -= 1
    return "".join(str_r)

class packet():

    def __init__(self, file = "1.pcap"):
        self.file = file
        self.ip_conv = self.conv_ip()
        self.ether_conv = self.conv_ether()
        self.ip_endpoints = self.endpoints_ip()
        self.ether_endpoints = self.endpoints_ether()
        self.len_packet = self.packet_len()
        self.protos = self.proto_Hierarchy()
        self.outline = self.packet_outline()

    def packet_outline(self):
        res = {}
        res['filed']=['数据包数','平均包长','平均每秒包数','物理地址数','IP地址数','物理会话','IP会话','链路层协议数','网络层协议数','传输层协议数','应用层协议数', '总协议数']
        value = [self.len_packet['frame_num'][0], self.len_packet['average_len'][0], ("%.2f" %(float(self.len_packet['rate'][0])*1000)), len(self.ether_endpoints['data'][0]), len(self.ip_endpoints['data'][0]), len(self.ether_conv['data'][0]), len(self.ip_conv['data'][0])]
        nProtos = []
        ip_index = 0
        for proto in self.protos:
            index = int(proto["priority"])
            if index + 1 > len(nProtos):
                for i in range(index + 1 - len(nProtos)):
                    nProtos.append([])
            if proto["proto"] not in nProtos[index]:
                nProtos[index].append(proto["proto"])
            if proto["proto"] == "ip" and ip_index == 0:
                ip_index = index
        sum = 0
        for i in range(4):
            sum += len(nProtos[ip_index - 1 + i])
            value.append(len(nProtos[ip_index - 1 + i]))
        value.append(sum)
        res['value'] = value
        return res

    def proto_Hierarchy(self):
        output = os.popen("{} -r {} -z io,phs -q".format(tshark_path, self.file)).read().strip()
        content = output.split("Filter:")[1].strip().strip("=").strip()
        line_list = []
        index = 1
        for line in content.splitlines():
            proto = line.split("frames:")
            frames = proto[1].split("bytes:")
            bytes_frame = frames[1].strip()
            priority = int((41 - len(proto[0].lstrip()))/2)
            line_dict = {"id":index, "pid": 0, "proto":proto[0].strip(),"frame_num":frames[0].strip(),"bytes":bytes_frame,"priority":priority}
            index += 1
            line_list.append(line_dict)

        for i in range(len(line_list)):
            cur_priority = line_list[i]["priority"]
            if cur_priority== 0 | i == 0:
                continue
            j = i - 1
            while j >= 0:
                if(line_list[j]["priority"] == cur_priority - 1):
                    line_list[i]["pid"] = line_list[j]["id"]
                    break
                j -= 1
        return line_list
    
    def packet_len(self):
        output = os.popen("{} -r {} -z plen,tree -q".format(tshark_path, self.file)).read().strip()
        content = output.split("Start")[1].strip().strip("-").strip()
        frame_num = []
        average_len = []
        min_len = []
        max_len = []
        rate = []
        percentage = []
        for line in content.splitlines():
            line_content = line.strip().split()
            if len(line_content) == 10:
                frame_num.append(line_content[2])
                average_len.append(line_content[3])
                min_len.append(line_content[4])
                max_len.append(line_content[5])
                rate.append(line_content[6])
                percentage.append(line_content[7])
            elif len(line_content) == 11:
                frame_num.append(line_content[3])
                average_len.append(line_content[4])
                min_len.append(line_content[5])
                max_len.append(line_content[6])
                rate.append(line_content[7])
                percentage.append(line_content[8])
            else :
                frame_num.append(line_content[1])
                average_len.append(line_content[2])
                min_len.append(line_content[3])
                max_len.append(line_content[4])
                rate.append(line_content[5])
                percentage.append(line_content[6])
        res = {'frame_num':frame_num, 'average_len':average_len, 'min_len':min_len, 'max_len':max_len, 'rate':rate, 'percentage':percentage}
        return res

    def conv_ip(self):
        output = os.popen("{} -r {} -z conv,ip -q".format(tshark_path, self.file)).read().strip()
        content = output.split('|')[-1].strip('=').strip().replace("<->",'').replace(",",'').splitlines()
        index = ["节点1","节点2","数据包(<-)","字节数(<-)","数据包(->)","字节数(->)","数据包(总)","字节数(总)","开始时间(相对)","持续时间"]
        data =[]
        for i in range(len(index)):
            data.append([])
        for line in content:
            line_content = line.split()
            if len(line_content) == 13:
                for i in range(3):
                    data[i].append(line_content[i])
                data[3].append(line_content[3]+line_content[4])
                data[4].append(line_content[5])
                data[5].append(line_content[6]+line_content[7])
                data[6].append(line_content[8])
                data[7].append(line_content[9]+line_content[10])
                data[8].append(line_content[11])
                data[9].append(line_content[12])
            elif len(line_content) == 10:
                for i in range(3):
                    data[i].append(line_content[i])
                data[3].append(line_content[3])
                data[4].append(line_content[4])
                data[5].append(line_content[5])
                data[6].append(line_content[6])
                data[7].append(line_content[7])
                data[8].append(line_content[8])
                data[9].append(line_content[9])
                
            # for i in range(len(line_content)):
            #     data[i].append(line_content[i])
        res = {'filed':index, 'data':data}
        return res

    def conv_ether(self):
        output = os.popen("{} -r {} -z conv,ether -q".format(tshark_path, self.file)).read().strip()
        content = output.split('|')[-1].strip('=').strip().replace("<->",'').replace(",",'').splitlines()
        index = ["节点1","节点2","数据包(<-)","字节数(<-)","数据包(->)","字节数(->)","数据包(总)","字节数(总)","开始时间(相对)","持续时间"]
        data =[]
        for i in range(len(index)):
            data.append([])
        for line in content:
            line_content = line.split()
            if len(line_content) == 13:
                for i in range(3):
                    data[i].append(line_content[i])
                data[3].append(line_content[3]+line_content[4])
                data[4].append(line_content[5])
                data[5].append(line_content[6]+line_content[7])
                data[6].append(line_content[8])
                data[7].append(line_content[9]+line_content[10])
                data[8].append(line_content[11])
                data[9].append(line_content[12])
            elif len(line_content) == 10:
                for i in range(3):
                    data[i].append(line_content[i])
                data[3].append(line_content[3])
                data[4].append(line_content[4])
                data[5].append(line_content[5])
                data[6].append(line_content[6])
                data[7].append(line_content[7])
                data[8].append(line_content[8])
                data[9].append(line_content[9])
            # for i in range(len(line_content)):
            #     data[i].append(line_content[i])
        res = {'filed':index, 'data':data}
        return res

    def endpoints_ip(self):
        output = os.popen("{} -r {} -z endpoints,ip -q".format(tshark_path, self.file)).read().strip()
        content = output.split('|')[-1].strip('=').strip().splitlines()
        index = ["IP","数据包","字节数","发送数据包","发送字节数","接收数据包","接收字节数"]
        data =[]
        for i in range(len(index)):
            data.append([])
        for line in content:
            line_content = line.split()
            for i in range(len(line_content)):
                data[i].append(line_content[i])
        res = {'filed':index, 'data':data}
        return res

    def endpoints_ether(self):
        output = os.popen("{} -r {} -z endpoints,ether -q".format(tshark_path, self.file)).read().strip()
        content = output.split('|')[-1].strip('=').strip().splitlines()
        index = ["节点","数据包","字节数","发送数据包","发送字节数","接收数据包","接收字节数"]
        data = []
        for i in range(len(index)):
            data.append([])
        for line in content:
            line_content = line.split()
            for i in range(len(line_content)):
                data[i].append(line_content[i])
        res = {'filed':index, 'data':data}
        return res
    
    def equal(self, packet):
        if self.file is packet.file:
            return True
        else:
            return False
    
    def add(self, packet):
        for i in range(len(self.ip_conv['data'])):
            self.ip_conv['data'][i].extend(packet.ip_conv['data'][i])
            self.ether_conv['data'][i].extend(packet.ether_conv['data'][i])
        for i in range(len(self.ip_endpoints['data'])):
            self.ip_endpoints['data'][i].extend(packet.ip_endpoints['data'][i])
            self.ether_endpoints['data'][i].extend(packet.ether_endpoints['data'][i])
        
        # 报文数量相加
        for i in range(len(self.len_packet['frame_num'])):
            len_before = int(self.len_packet['frame_num'][i])
            len_add = int(packet.len_packet['frame_num'][i])
            len_after = len_before + len_add
            if len_add == 0:
                continue
            elif len_before == 0:
                self.len_packet['frame_num'][i] = str(len_add)
                self.len_packet['average_len'][i] = packet.len_packet['average_len'][i]
                self.len_packet['min_len'][i] = packet.len_packet['min_len'][i]
                self.len_packet['max_len'][i] = packet.len_packet['max_len'][i]
                self.len_packet['rate'][i] = packet.len_packet['rate'][i]
                self.len_packet['percentage'][i] = packet.len_packet['percentage'][i]
            else:
                self.len_packet['frame_num'][i] = str(len_after)
                self.len_packet['average_len'][i] = (1 + float(len_add) / len_before) * float(self.len_packet['average_len'][i]) \
                    + (1 + float(len_before) / len_add) * float(packet.len_packet['average_len'][i])
                len_min = min(int(self.len_packet['min_len'][i]),int(packet.len_packet['min_len'][i]))
                self.len_packet['min_len'][i] = str(len_min)
                len_max = max(int(self.len_packet['max_len'][i]),int(packet.len_packet['max_len'][i]))
                self.len_packet['max_len'][i] = str(len_max)
                duration = len_before / float(self.len_packet['rate'][i]) + len_add / float(packet.len_packet['rate'][i])
                self.len_packet['rate'][i] = str(len_after / duration)
                self.len_packet['percentage'][i] = "%.2f%%" % (len_after / float(self.len_packet['frame_num'][0]) * 100.0)

        #协议
        for i in range(len(packet.protos)):
            dict_tmp = packet.protos[i]
            exist = False
            for j in range(len(self.protos)):
                if dict_tmp["priority"] == self.protos[j]["priority"] and dict_tmp["proto"] == self.protos[j]["proto"]:
                    #frames和bytes相加
                    self.protos[j]["frame_num"] = add_str(self.protos[j]["frame_num"], dict_tmp["frame_num"])
                    self.protos[j]["bytes"] = add_str(self.protos[j]["bytes"], dict_tmp["bytes"])
                    exist = True
                    packet.protos[i]["id"] = self.protos[j]["id"]
                    break
            if not exist:
                if dict_tmp["priority"] == 0:
                    packet.protos[i]["id"] = len(self.protos) + 1
                    self.protos.append(packet.protos[i])
                else:
                    p = packet.protos[dict_tmp["pid"]]["id"] + 1
                    p_p = p - 1
                    p_pr = packet.protos[dict_tmp["pid"]]["priority"]
                    while p < len(self.protos):
                        if self.protos[p]["priority"] <= p_pr:
                            break
                        p = p + 1
                    packet.protos[i]["id"] = p
                    packet.protos[i]["pid"] = p_p
                    self.protos.insert(p, packet.protos[i])
                    for j in range(p+1, len(self.protos)):
                        self.protos[j]["id"] += 1
                        if self.protos[j]["pid"] > p_p:
                            self.protos[j]["pid"] += 1
        
        #摘要
        self.outline = self.packet_outline()