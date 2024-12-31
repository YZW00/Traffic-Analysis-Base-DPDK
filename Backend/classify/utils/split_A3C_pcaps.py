'''
功能:基于已有conf.json文件(用于指定哪个进程属于哪个类别，需事先人工写入), 将A3C产出目录dst_path下的pcap文件按类别分开至 dst_path
参数:pcap文件所在目录pcapsDir, 特征及标签csv的保存目录saveDir, 长度序列的长度flow_seq_len
输出:在saveDir下新建目录,并生成统计特征csv、长度序列文件csv、标签文件csv
python3 split_A3C_pcaps.py ./conf.json "../dataset/A3C_pcaps/2022-12-13 17:55:19" "../dataset/A3C_pcaps/2022-12-14 15:48:41" ../dataset/pcaps
'''
import os, shutil, json
import argparse

class SplitA3C:
    def __init__(self, json_path, pcap_root, dst_path):
        self.json_path = json_path
        self.pcap_root = pcap_root
        self.dst_path = dst_path
        self.maxNum_class = {}
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

    def get_max_num_class(self, dst_path):
        for Type in os.listdir(dst_path):
            if os.path.isdir(os.path.join(dst_path, Type)):
                for pcap in os.listdir(os.path.join(dst_path, Type)):
                    try:
                        n = int(pcap.split('.')[0])
                        if Type not in self.maxNum_class.keys():
                            self.maxNum_class[Type] = n
                        elif self.maxNum_class[Type] < n:
                            self.maxNum_class[Type] = n
                    except:
                        print('warning: pcap文件命名不规范')

    def split_A3C_pcaps(self, json_path, pcap_root):
        with open(json_path, 'r') as f:
            conf = json.load(f)
        
        reverse_dict = dict()
        for c, v in conf.items():
            for prcess in v:
                reverse_dict[prcess] = c

        for pcap_dir in pcap_root:
            # if os.path.isdir(os.path.join(pcap_root, pcap_dir)):
            for process in os.listdir(pcap_dir):
                processName = process.split('.', 1)[0]
                if processName in reverse_dict.keys():
                    class_name = reverse_dict[processName]
                    # print("processName: {}".format(processName))
                    dst_dir = os.path.join(self.dst_path, class_name)
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                    
                    if class_name not in self.maxNum_class.keys():
                        shutil.copyfile(os.path.join(pcap_dir, process), os.path.join(dst_dir, '1.pcap'))
                        self.maxNum_class[class_name] = 1
                    else:
                        self.maxNum_class[class_name] += 1
                        shutil.copyfile(os.path.join(pcap_dir, process), os.path.join(dst_dir, '{}.pcap'.format(self.maxNum_class[class_name])))
        print('划分完成!')
    
    def run(self):
        try:
            self.get_max_num_class(self.dst_path)
            self.split_A3C_pcaps(self.json_path, self.pcap_root)
            return {'status': "success"}
        except Exception as e:
            return {'status': 'fail', 'error':str(e)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('json_path')
    parser.add_argument('pcap_root', nargs='+')
    parser.add_argument('dst_path')

    args = parser.parse_args()
    json_path = args.json_path
    pcap_root = args.pcap_root
    dst_path = args.dst_path
    print('pcap_root', pcap_root)
    splitA3C = SplitA3C(json_path, pcap_root, dst_path)
    result = splitA3C.run()
    print(result)