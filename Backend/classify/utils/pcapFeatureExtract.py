'''
功能:基于数据集pcaps 目录下的pcap文件, 提取流统计特征和流长度序列, 并生成标签文件. 用于训练分类模型
参数:pcap文件所在目录pcapsDir, 特征及标签csv的保存目录saveDir, 长度序列的长度flow_seq_len
输出:在saveDir下新建目录,并生成统计特征csv、长度序列文件csv、标签文件csv
python3 pcapFeatureExtract.py ../dataset/pcaps/c1 ../dataset/pcaps/c2  ../dataset/Features/tmp 24
'''

import argparse
import dpkt
import os, sys
import pandas as pd
import numpy as np
import ipaddress

# saveDir = r'./dataset/Length-Sequnce'
# pcapsDir = r'./dataset/Pcap'
# python3 pcapLenSeqExtract.py /mnt/sda1/xxx/Dataset/classesnew/tcp ../dataset/Features 24

class PcapFeatureExtract:
    def __init__(self, pcapsDir, saveDir, flow_seq_len):
        self.pcapsDir = pcapsDir
        self.saveDir = saveDir
        self.flow_seq_len = flow_seq_len
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        # if not os.path.exists(pcapsDir):
        #     os.makedirs(pcapsDir)
        self.name_line = ['src_IP', 'dst_IP', 'src_port', 'dst_port', 'trans_proto', 'pkt_num', 'total_Bytes', 'duration']

    def pcap_read(self, pcapFileName):
        noLinkLayer = False
        ipPktList = []
        tsList = []
        fd = open(pcapFileName, 'rb')
        # 兼容pcap和pcapng
        magic_head = fd.read(4)
        fd.seek(0, 0)
        pcapReader = None
        # print('pcapFileName:', pcapFileName)
        try:
            if magic_head == b'\xd4\xc3\xb2\xa1': # pcap文件头
                pcapReader = dpkt.pcap.Reader(fd)
            else:
                pcapReader = dpkt.pcapng.Reader(fd)
            # 兼容没有链路层的pcap
            if pcapReader.datalink() == 101:
                noLinkLayer = True
            if noLinkLayer:
                for (ts, buf) in pcapReader.readpkts():  # (时间戳,包)
                    try:
                        if buf[0] == 0x60: # ipv6
                            continue
                        else:
                            ip = dpkt.ip.IP(buf)
                        ipPktList.append(ip)
                        tsList.append(ts)
                    except Exception as e:
                        print("No link layer:{}".format(e))
            else:
                for (ts, buf) in pcapReader.readpkts():
                    try:
                        eth = dpkt.ethernet.Ethernet(buf)
                        if eth.type != dpkt.ethernet.ETH_TYPE_IP and eth.type != dpkt.ethernet.ETH_TYPE_IP6:
                            continue
                        ip = eth.data
                        if type(ip) is bytes:
                            if eth.type == dpkt.ethernet.ETH_TYPE_IP: # ipv4
                                ip = dpkt.ip.IP(buf)
                            elif eth.type == dpkt.ethernet.ETH_TYPE_IP6: # ipv6
                                ip = dpkt.ip6.IP6(buf)
                        ipPktList.append(ip)
                        tsList.append(ts)
                    except Exception as e:
                        print("Normal layer:{}".format(e))
        
        except Exception as e:
            print("Error: 文件为空或格式有误！")
        
        return ipPktList, tsList

    def flow_extraction_TCP(self, ipPktList, tsList):
        '''
        flow_dict = {
            key: (src_IP, dst_IP, src_port, dst_port, trans_proto)
            value: ([pkt_num, total_Bytes, ts_start, ts_end], [pkt_len1, pkt_len2, ...])
        }
        '''
        flow_dict = dict({})
        for ipPkt, ts in zip(ipPktList, tsList):
            if ipPkt.p is not dpkt.ip.IP_PROTO_TCP:
                continue
            tcp = ipPkt.data
            key = (ipPkt.src, ipPkt.dst, tcp.sport, tcp.dport, ipPkt.p)
            # 初始化
            if key not in flow_dict.keys():
                # print('key:', str(key[0],encoding='Unicode'))
                flow_dict[key] = ([0, 0, None, None], [])
            # pkt_num
            flow_dict[key][0][0] += 1
            # total_Bytes
            flow_dict[key][0][1] += len(tcp.data)
            # ts_start
            if flow_dict[key][0][2] is None:
                flow_dict[key][0][2] = ts
            else:
                flow_dict[key][0][2] = min(flow_dict[key][0][2], ts)
            # ts_end
            if flow_dict[key][0][3] is None:
                flow_dict[key][0][3] = ts
            else:
                flow_dict[key][0][3] = max(flow_dict[key][0][3], ts)
            # len_seq
            if len(flow_dict[key][1]) < self.flow_seq_len:
                flow_dict[key][1].append(len(tcp.data))
        return flow_dict
    
    def run(self):
        try:
            print('{} 流特征提取...'.format(self.pcapsDir))
            # suffix = self.pcapsDir.split('/')[-1] if self.pcapsDir[-1] != '/' else self.pcapsDir.split('/')[-2]
            # saveDir = os.path.join(self.saveDir, suffix)
            # if not os.path.exists(self.saveDir):
            #     os.makedirs(saveDir)
            classNote = open("{}/ClassesInfo.txt".format(self.saveDir), 'w', encoding='utf-8')

            statistical_fea = []    # 统计特征
            len_seq = []            # 长度序列特征
            label_list = []         # 标签(进程)
            class_tag = 0           # 类别标签
            for serviceDir in self.pcapsDir:
                # serviceDir = os.path.join(self.pcapsDir, serviceClass)
                classNote.write("{}:{}\n".format(class_tag, serviceDir.split('/')[-1]))
                for pcapFile in os.listdir(serviceDir):
                    if not pcapFile.endswith('.pcap') and not pcapFile.endswith('.pcapng'):
                        continue
                    print('正在处理文件:{}'.format(pcapFile))
                    # label = pcapFile.split('.')[0]
                    pDir = os.path.join(serviceDir, pcapFile)
                    ipPktList, tsList = self.pcap_read(pDir)
                    tmpFlows = self.flow_extraction_TCP(ipPktList, tsList)
                    for key, value in tmpFlows.items():
                        if len(value[1]) < self.flow_seq_len:
                            continue
                        key = list(key)
                        statistical_fea.append([ipaddress.ip_address(key[0]), ipaddress.ip_address(key[1])] + key[2:5] + value[0][:2] + [value[0][3] - value[0][2]])
                        len_seq.append(value[1])
                        label_list.append(class_tag)
                class_tag += 1
            
            classNote.close()
            
            pd.DataFrame(statistical_fea, columns=self.name_line).to_csv(os.path.join(self.saveDir, "statistical.csv"), index=False, header=False)
            np.savetxt('{}/lenSeq.csv'.format(self.saveDir), np.array(len_seq, dtype = np.int64), delimiter = ',')
            pd.DataFrame(label_list).to_csv(os.path.join(self.saveDir, "label.csv"), index=False, header=False)
            print('Finish! Saved to {}'.format(self.saveDir))
            return {'status': "success"}
        except Exception as e:
            return {'status': 'fail', 'error':str(e)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pcap特征提取所需参数')
    parser.add_argument('pcapsDir', nargs='+',  help="pcap业务类的选择目录")
    parser.add_argument('saveDir',  help="输出目录")
    parser.add_argument('flow_seq_len', type=int, help="长度序列")
    
    args = parser.parse_args()
    pcapsDir = args.pcapsDir
    saveDir = args.saveDir
    flow_seq_len = args.flow_seq_len

    extractor = PcapFeatureExtract(pcapsDir, saveDir, flow_seq_len)
    result = extractor.run()
    print(result)



    