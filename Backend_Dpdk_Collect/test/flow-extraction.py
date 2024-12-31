import argparse
import datetime
import glob
import os
import zlib

import brotli
import dpkt
import numpy


# python3 flow-extraction.py B站 44 tls B站-漫画-21.pcap B站-漫画-22.pcap B站-漫画-23.pcap B站-漫画-24.pcap B站-漫画-25.pcap

# saveDir = r'../dataset/Length-Sequence'
# pcapsDir = r'../dataset/Pcap'
# if not os.path.exists(saveDir):
#     os.mkdir(saveDir)
# if not os.path.exists(pcapsDir):
#     os.mkdir(pcapsDir)

Decompress = False

parser = argparse.ArgumentParser(description='流提取')
parser.add_argument('flow_seq_len', type=int, help="长度序列总长")
parser.add_argument('protocol', help="可选http, tls, tcp")
parser.add_argument('pcap_path', help="pcap文件路径, 支持glob模式匹配")
parser.add_argument('dst_dir', help=" 提取后特征文件的存放目录")

args = parser.parse_args()
flow_seq_len = args.flow_seq_len
protocol = args.protocol
pcap_path_glob = args.pcap_path  # glob模式的文件路径
dst_dir = args.dst_dir


def pcap_read(pcap_file_name):
    noLinkLayer = False
    ipPktList = []
    fd = open(pcap_file_name, 'rb')
    # 兼容pcap和pcapng
    try:
        pcapReader = dpkt.pcap.Reader(fd)
    except Exception as e:
        fd.seek(0, 0)
        pcapReader = dpkt.pcapng.Reader(fd)
    # 兼容没有链路层的pcap
    if pcapReader.datalink() == 101:
        noLinkLayer = True
    if noLinkLayer:
        for (ts, buf) in pcapReader.readpkts():  # (时间戳，包)
            try:
                if buf[0] == 0x60:
                    # ip = dpkt.ip6.IP6(buf)
                    # Ipv6的流量为A3C和服务器通信流量，应用流量全为Ipv4
                    continue
                else:
                    ip = dpkt.ip.IP(buf)
                dstIp = int(ip.dst.hex(), 16)
                # 过滤LLMNR SSDP
                if 0xE00000FF <= dstIp <= 0xEFFFFFFF:
                    continue
                ipPktList.append(ip)
            except Exception as e:
                print("No link layer:{}".format(e))
    else:
        for (ts, buf) in pcapReader.readpkts():
            try:
                eth = dpkt.ethernet.Ethernet(buf)
                # 过滤NBNS
                if eth.dst == b'\xff\xff\xff\xff\xff\xff':
                    continue
                ip = eth.data
                dstIp = int(ip.dst.hex(), 16)
                # 过滤LLMNR SSDP
                if 0xE00000FF <= dstIp <= 0xEFFFFFFF:
                    continue
                ipPktList.append(ip)
            except Exception as e:
                print("Normal layer:{}".format(e))
    fd.close()
    return ipPktList


def flow_extraction_UDP(pcap_file_name):
    # print("pcapFileName:{}".format(pcapFileName))
    ipPktList = pcap_read(pcap_file_name)
    flow_dict = dict({})  # 用于保存流的包长序列

    for ipPkt in ipPktList:
        if ipPkt.p is not dpkt.ip.IP_PROTO_UDP:
            continue
        udp = ipPkt.data
        if type(udp) == type(b'a'):
            continue
        if udp.sport == 53 or udp.dport == 53:
            continue
        if udp.sport > udp.dport:
            key = (ipPkt.src, udp.sport, ipPkt.dst, udp.dport, ipPkt.p)
        else:
            key = (ipPkt.dst, udp.dport, ipPkt.src, udp.sport, ipPkt.p)

        if key not in flow_dict.keys():
            flow_dict[key] = []

        flow_dict[key].append(len(udp.data) * (1 if udp.sport > udp.dport else -1))
    return list(flow_dict.values())


def flow_extraction_HTTP(pcap_file_name):
    # 该func针对从OSI-7导出的pcap进行处理
    # print("pcapFileName:{}".format(pcapFileName))
    flow_dict = dict({})
    Preface_Exist = False  # HTTP2 的preface标记
    http2_stream = {}
    tmp_pre = -1
    fd = open(pcap_file_name, 'rb')
    # 兼容pcap和pcapng
    try:
        pcapReader = dpkt.pcap.Reader(fd)
    except Exception as e:
        fd.seek(0, 0)
        pcapReader = dpkt.pcapng.Reader(fd)

    for (ts, buf) in pcapReader.readpkts():
        # proto = "http" if buf[2:4] == b'\x00\x10' else "http2"
        proto = 'http2' if buf[4:9] == b'http2' else 'http'
        iter = 4 + int(buf[2:4].hex(), 16) + 2
        ip_len, ip_version = (4, "ipv4") if buf[iter:iter + 2] == b'\x00\x04' else (16, "ipv6")
        iter += 2
        http = {'src': buf[iter:iter + ip_len].hex(), 'dst': buf[iter + ip_len + 4:iter + 2 * ip_len + 4].hex()}
        iter = iter + 2 * ip_len + 4 + 12
        http['sport'], http['dport'] = (int(buf[iter:iter + 4].hex(), 16), int(buf[iter + 8:iter + 12].hex(), 16))
        http['proto'] = proto
        buf = buf[iter + 12 + 12:]

        # 提取有效载荷长度
        # HTTP 1.X
        if proto == 'http':
            tmp_buf = b''
            flag = b''
            for i in range(0, len(buf) - 3):
                if buf[i:i + 4] == b'\r\n\r\n':
                    tmp_buf = buf[:i]
            for i in range(0, len(tmp_buf) - 1):
                if tmp_buf[i:i + 2] == b'\r\n':
                    flag = tmp_buf[:i]
                    tmp_buf = tmp_buf[i + 2:]
                    break
            http_head = dpkt.http.Message()
            http_head.unpack(tmp_buf, False)
            # 有"content-length"字段直接用
            data_len = int(http_head.headers['content-length']) if 'content-length' in http_head.headers else -1
            if data_len == -1:
                # Response
                if flag[:4] == b'HTTP':
                    try:
                        http['pkt'] = dpkt.http.Response(buf)
                        # data_len = len(http['pkt'].body)
                        # print(data_len)
                    except dpkt.UnpackError:
                        # print('{} Error:'.format(pcapFileName),e)
                        continue
                # Request
                else:  # flag[:4] == b'POST' or flag[:3] == b'GET':
                    try:
                        http['pkt'] = dpkt.http.Request(buf)
                        # data_len = len(http['pkt'].uri + http['pkt'].method)
                        # print('head',data_len)
                        # print(http['pkt'])
                    except Exception as e:
                        print('{} Error:'.format(pcap_file_name), e)
                        return list()
                # else:
                #     print('Error:无法识别http类型')
                # 数据有压缩则解压
                if Decompress and data_len != 0 and 'content-encoding' in http['pkt'].headers.keys():
                    Encoding = http['pkt'].headers['content-encoding']
                    if Encoding == 'br':
                        data_len = len(brotli.decompress(http['pkt'].body))
                    else:  # gzip, deflate
                        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
                        data_len = len(decompressor.decompress(http['pkt'].body))
                else:
                    data_len = len(http['pkt'].body)
            # 写入flow_dict
            if http['sport'] > http['dport']:  # 发出的包
                tmp_pre = -1
                key = (http['src'], http['sport'], http['dst'], http['dport'], http['proto'])
                idx = 0
            else:  # 收到的包
                if data_len == tmp_pre:
                    continue
                else:
                    tmp_pre = data_len
                key = (http['dst'], http['dport'], http['src'], http['sport'], http['proto'])
                idx = 1
            if key not in flow_dict.keys():
                flow_dict[key] = []
            flow_dict[key].append(data_len * (1 if idx == 0 else -1))
        # HTTP2
        elif proto == 'http2':
            if not Preface_Exist:
                try:
                    Frames, index = dpkt.http2.frame_multi_factory(buf, True)
                    Preface_Exist = True
                except Exception as e:
                    # print('{} Warning:'.format(pcapFileName), e)
                    Frames, index = dpkt.http2.frame_multi_factory(buf, False)
            else:
                try:
                    Frames, index = dpkt.http2.frame_multi_factory(buf, False)
                except Exception as e:
                    Frames, index = dpkt.http2.frame_multi_factory(buf, True)
            # print(Frames)
            data_len = 0
            Payload_flag = False
            for frame in Frames:
                if not frame.stream_id:
                    continue
                elif isinstance(frame, dpkt.http2.HeadersFrame):
                    if http['sport'] > http['dport']:
                        Payload_flag = True
                        if frame.stream_id not in http2_stream.keys():
                            http2_stream[frame.stream_id] = 0
                        else:
                            continue
                    else:
                        pass
                elif isinstance(frame, dpkt.http2.DataFrame):
                    http2_stream[frame.stream_id] += frame.length
                    if frame.flags & dpkt.http2.HTTP2_FLAG_PADDED:
                        http2_stream[frame.stream_id] -= frame.pad_length + 1
                    if frame.flags & dpkt.http2.HTTP2_FLAG_END_STREAM:
                        # print('End of {}: {}'.format(frame.stream_id,http2_stream[frame.stream_id]))
                        data_len = http2_stream[frame.stream_id]
                        Payload_flag = True
            if not Payload_flag:
                continue
            else:
                # 写入flow_dict
                if http['sport'] > http['dport']:  # 发出的包
                    key = (http['src'], http['sport'], http['dst'], http['dport'], http['proto'])
                    idx = 0
                else:  # 收到的包
                    key = (http['dst'], http['dport'], http['src'], http['sport'], http['proto'])
                    idx = 1
                if key not in flow_dict.keys():
                    flow_dict[key] = []
                flow_dict[key].append(data_len * (1 if idx == 0 else -1))
    # print(flow_dict.values())
    return list(flow_dict.values())


def flow_extraction_TLS(pcap_file_name):
    # print("pcapFileName:{}".format(pcapFileName))
    ipPktList = pcap_read(pcap_file_name)
    flow_dict = dict({})
    resume_data_dict = dict({})
    seq_set = set()

    for ipPkt in ipPktList:
        # 过滤非TCP
        if ipPkt.p is not dpkt.ip.IP_PROTO_TCP:
            continue
        tcp = ipPkt.data
        if len(tcp.data) <= 1:  # 过滤 keep-alive len = 1, ack len = 0
            continue
        # 发出去的包
        if tcp.sport > tcp.dport:
            key = (ipPkt.src, tcp.sport, ipPkt.dst, tcp.dport, ipPkt.p)
            idx = 0
        # 收到的包
        else:
            key = (ipPkt.dst, tcp.dport, ipPkt.src, tcp.sport, ipPkt.p)
            idx = 1
            # 虚假重传过滤 spurious retransmission
            if tcp.seq in seq_set:
                continue
            seq_set.add(tcp.seq)

        if key not in flow_dict.keys():
            flow_dict[key] = []  # 不分方向流
            resume_data_dict[key] = [b'', b'']  # 根据key拆分双向流

        data = resume_data_dict[key][idx] + tcp.data
        # print("new tcp-data:", len(tcp.data))

        while len(data) > 5:
            try:
                record_len = int(data[3:5].hex(), 16)
                # 说明还需要下一个TCP片段补充完整的TLS
                if record_len > len(data) - 5:
                    break
                else:
                    tls = dpkt.ssl.TLS(data[:record_len + 5])
                    # print("Type::", tls.data)
                    data = data[record_len + 5:]
                    flow_dict[key].append(tls.len * (1 if idx == 0 else -1))
            except Exception as e:
                print("record_len:{}, sport:{}, dport:{},error:{}".format(data[3:5], tcp.sport, tcp.dport, e))
        resume_data_dict[key][idx] = data
    # print(len(list(flow_dict.values())[0]))
    return list(flow_dict.values())


def flow_extraction_TCP(pcap_file_name):
    # print("pcapFileName:{}".format(pcapFileName))
    ipPktList = pcap_read(pcap_file_name)
    flow_dict = dict({})
    for ipPkt in ipPktList:
        if ipPkt.p is not dpkt.ip.IP_PROTO_TCP:
            continue
        tcp = ipPkt.data
        if type(tcp) == type(b'a'):
            continue
        if len(tcp.data) == 0:
            continue
        if tcp.sport > tcp.dport:
            key = (ipPkt.src, tcp.sport, ipPkt.dst, tcp.dport, ipPkt.p)
        else:
            key = (ipPkt.dst, tcp.dport, ipPkt.src, tcp.sport, ipPkt.p)
        if key not in flow_dict.keys():
            flow_dict[key] = []
        flow_dict[key].append(len(tcp.data) * (1 if tcp.sport > tcp.dport else -1))
    return list(flow_dict.values())


# 若数据流长>flow_seq_len，则截取前flow_seq_len为结果，若不够则返回None
def ngram_extraction(flow_list):
    ngramRes = []
    for flow in flow_list:
        if len(flow) < flow_seq_len:
            continue
        else:
            ngramRes.append(flow[:flow_seq_len])
    return ngramRes


def extract_from_app(flow_extraction_method, app_dir):
    appRes = []
    for pcap_file in os.listdir(app_dir):  # app目录的所有pcap
        tmp_res = flow_extraction_method(os.path.join(app_dir, pcap_file))  # 获取数据，客户端收到负数，发送正数
        tmp_res = ngram_extraction(tmp_res)
        appRes += tmp_res
    return appRes


def main():
    print(flow_seq_len, protocol, pcap_path_glob, dst_dir)

    pcap_paths = glob.glob(pcap_path_glob)
    if len(pcap_paths) == 0:
        print("未找到匹配的文件路径")
        return

    flow_extraction_method = None
    if protocol == "udp":
        flow_extraction_method = flow_extraction_UDP
    elif protocol == "tls":
        flow_extraction_method = flow_extraction_TLS
    elif protocol == "tcp":
        flow_extraction_method = flow_extraction_TCP
    elif protocol == "http":
        flow_extraction_method = flow_extraction_HTTP
    else:
        print("未解析的协议: {}！".format(protocol))
        return

    print('{} 长度序列提取...'.format(protocol))
    lastRes = []
    for pcap_path in pcap_paths:
        tmpRes = flow_extraction_method(pcap_path)
        tmpRes = ngram_extraction(tmpRes)
        lastRes += tmpRes

    print("saving...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_dir = os.path.join(dst_dir, "{}_{}".format(protocol, timestamp))
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    numpy.savetxt('{}/{}_{}.csv'.format(save_dir, protocol, timestamp), numpy.array(lastRes, dtype=numpy.int64),
                  delimiter=',')

    print('finish, save to {}'.format(timestamp))


if __name__ == '__main__':
    main()
