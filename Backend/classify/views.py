from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
from django.db.models import Sum, Avg, Max, Min
import ipaddress
import random
import json, os, time
from .utils.getClassInfo import getClassInfo
from .utils.classic_pred import Classic_Pred
from .utils.classic_train import Classic_Train
from .utils.RNN import RNN
from .utils.lstmNet_pred import LSTM_Pred
from .utils.lstmNet_train import LSTM_Train
from .utils.united_pred import United_Pred
from .utils.split_A3C_pcaps import SplitA3C
from .utils.pcapFeatureExtract import PcapFeatureExtract
from .utils.classic_pred_from_mysql import Classic_Pred_MySQL
from .utils.lstmNet_pred_mysql import LSTM_Pred_MySQL
from .utils.united_pred_mysql import United_Pred_MySQL
import subprocess
from .models import Flowtables

# Create your views here.
def index(request):
    return HttpResponse("Hello, You're at the classify index.")

'''
功能: 展示dataset的相关目录及文件
GET: 返回dataset根目录 ".dataset/" 下的所有子目录名
POST: 进入子目录。
    参数 "childDir" 多级子目录字符串，如 "2022-12-13 17:55:19", 此时返回目录"A3C_pcaps/2022-12-13 17:55:19"下的所有文件名
    {
        "childDir":"2022-12-13 17:55:19"
    }
    返回json字段: status: success / fail, result: 子目录名或文件名列表
'''
def show_dir(request):
    rootDir = './classify/dataset'
    if request.method == 'GET':
        result = os.listdir(rootDir)
        return HttpResponse(json.dumps({'status': 'success', 'result': result}), content_type='application/json')
    elif request.method == 'POST':
        try:
            rb = json.loads(request.body)
            childDir = rb['childDir']
            rootDir = os.path.join(rootDir, childDir)
            # A3C_dir 则过滤掉非目录
            result = os.listdir(rootDir)
            if childDir.rsplit('/', 1)[-1] == 'A3C_pcaps':
                result = list(filter(lambda x: os.path.isdir(os.path.join(rootDir, x)), result))
            
            return HttpResponse(json.dumps({'status': 'success', 'result': result}), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}))
    else:
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')

'''
功能: csv 业务分类模型预测
POST: 
    参数 "method": 模型类别 ,可选"classic / lstm / united"; 
    参数 "dataset_dir": Features下的数据集目录名, 如 "tcp";
    参数 "threshold": 阈值, 如 "0.5"
    返回json字段: status: success / fail, result: 预测结果字典， 包含"pred"、"prob"、"time"、"status"字段
'''
def model_pred_csv(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')
    try:
        rb = json.loads(request.body)
        method = rb['method'] # classic / lstm / united
        dataset_dir = rb['dataset_dir'] # tcp
        threshold = float(rb['threshold']) # 0.5

        model_dir = './classify/weights'
        dataset_dir = os.path.join('./classify/dataset/Features', dataset_dir)

        pred_model = None
        class_dict = getClassInfo(os.path.join(dataset_dir, 'ClassesInfo.txt'))
        if method == 'classic':
            pred_model = Classic_Pred(dataset_dir, model_dir, threshold, class_dict)
        elif method == 'lstm':
            pred_model = LSTM_Pred(dataset_dir, model_dir, threshold, class_dict)
        elif method == 'united':
            pred_model = United_Pred(dataset_dir, model_dir, threshold, class_dict)
        
        result_json = pred_model.pred()

        return HttpResponse(json.dumps({'status': 'success', 'result': result_json}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')

'''
功能: csv 业务分类模型训练
POST: 
    表单参数 "method": 模型类别 ,可选"classic / lstm"; 
    参数 "dataset_dir": Features下的数据集目录名, 如 "tcp";
    返回json字段: status: success / fail, result: 训练结果字典， 包含"f1"、"accuracy"、 "precision"、"recall"、 "time"、"status"字段
'''
def model_train_csv(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')
    try:
        rb = json.loads(request.body)
        method = rb['method'] # classic / lstm
        dataset_dir = rb['dataset_dir'] # tcp

        # method = request.POST.get('method') # classic / lstm
        # dataset_dir = request.POST.get('dataset_dir') # tcp
        model_dir = './classify/weights'
        dataset_dir = os.path.join('./classify/dataset/Features', dataset_dir)

        train_model = None
        class_dict = getClassInfo(os.path.join(dataset_dir, 'ClassesInfo.txt'))
        if method == 'classic':
            train_model = Classic_Train(dataset_dir, model_dir)
        elif method == 'lstm':
            train_model = LSTM_Train(dataset_dir, model_dir, class_dict)
        
        result_json = train_model.train()

        return HttpResponse(json.dumps({'status': 'success', 'result': result_json}), content_type='application/json')
    
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')

'''
功能: 执行A3C程序, 待完成。
'''
def A3C_run(request):
    SUDO_PASSWORD = '【Your_password】'
    A3C_dir = './classify/dataset/A3C_pcaps/A3C_Linux'
    '''
    if request.method == 'GET':
        try:
            A3C_pro = subprocess.Popen([A3C_dir], stdin=subprocess.PIPE , stderr=subprocess.PIPE)
            try:
                outs, errs = A3C_pro.communicate(timeout=3)
                print(outs)
                outs = outs.decode('utf-8')
            except subprocess.TimeoutExpired:
                A3C_pro.kill()
                outs, errs = A3C_pro.communicate()
                # print(outs)
                # outs = outs.decode('utf-8')
            return HttpResponse(json.dumps({'status': 'success', 'result':outs}))
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}))
    '''
    if request.method == 'POST':
        rb = json.loads(request.body)
        action = rb['action'] # start / stop
        if action == 'start':
            net_interface_id = int(rb['net_interface_id']) # 1
            A3C_pro = subprocess.Popen(['echo {} | sudo -S {}'.format(SUDO_PASSWORD, A3C_dir)], stdin=subprocess.PIPE)
            # A3C_pro.stdin.write('wyz646999@seu\n'.encode('utf-8'))
            # A3C_pro.communicate('{}\n'.format(net_interface_id).encode('utf-8'), timeout=5)
            A3C_pro.stdin.write('{}\n'.format(net_interface_id).encode('utf-8'))
            A3C_pro.stdin.flush()
            return HttpResponse(json.dumps({'status': 'success', 'pid': A3C_pro.pid}), content_type='application/json')
        elif action == 'stop':
            pid = int(rb['pid'])
            subprocess.Popen(['echo {} | sudo -S'.format(SUDO_PASSWORD), 'kill -9', pid])
            # os.kill(int(pid), signal.SIGKILL)
            return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')

'''
功能: 查看 / 修改 业务类别映射信息
GET: 返回业务类别映射信息
POST: 
    Json参数 "data": 业务类别映射信息(json格式)
    返回json字段: status: success / fail, result: 修改后的业务类别映射信息
'''
def split_config(request):
    confJson_path = './classify/config/conf.json'
    if request.method == 'GET':
        try:
            with open(confJson_path, 'r') as f:
                confJson = json.load(f)
            return HttpResponse(json.dumps({'status': 'success', 'result': confJson}), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')
    elif request.method == 'POST':
        try:
            rb = json.loads(request.body)
            newConfJson = rb['data']
            with open(confJson_path, 'w') as f:
                json.dump(newConfJson, f)
            return HttpResponse(json.dumps({'status': 'success', 'result': newConfJson}), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')

'''
功能: 将A3C采集的pcap文件按照给定业务类别划分
POST:
    Json参数 "pcap_dirs": 需要划分的pcap文件夹列表, 是./dataset/A3C_pcaps下的文件夹名, 例如: ['2022-12-13 17:55:19', '2022-12-14 15:48:41']
    返回json字段: status: success / fail
'''
def pcap_split(request):
    A3C_pcaps_root = './classify/dataset/A3C_pcaps'
    if request.method == 'POST':
        try:
            rb = json.loads(request.body)
            pcap_select = rb['pcap_dirs']
            pcap_paths = [os.path.join(A3C_pcaps_root, pcap_dir) for pcap_dir in pcap_select]
            print(pcap_paths)
            splitA3C = SplitA3C('./classify/config/conf.json', pcap_paths, './classify/dataset/pcaps')
            result = splitA3C.run()
            return HttpResponse(json.dumps(result), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')


'''
功能: 业务pcaps特征提取(即数据集构建)
POST:
    Json参数 "classes": 纳入数据集的业务名称列表, 是./classify/dataset/pcaps下的文件夹名, 例如: ['p2p', 'chat']
    Json参数 "dataset_name": 数据集名称, 例如: 'my_dataset', 则所生成的数据集文件夹路径为: ./dataset/Features/my_dataset
    返回json字段: status: success / fail
'''
def pcap_feature_extract(request):
    if request.method == 'POST':
        try:
            rb = json.loads(request.body)
            class_select = rb['classes']
            class_paths = [os.path.join('./classify/dataset/pcaps', pcap_dir) for pcap_dir in class_select]
            # print(class_paths)
            dataset_name = rb['dataset_name']
            dataset_path = os.path.join('./classify/dataset/Features', dataset_name)
            pcapFeaExtractor = PcapFeatureExtract(class_paths, dataset_path, 24)
            result = pcapFeaExtractor.run()
            return HttpResponse(json.dumps(result), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')

# 获取数据库流特征
def get_flow_table(request):
    # 默认返回最新的50条数据
    if request.method == 'GET':
        flows_fea = Flowtables.objects.order_by('-time')[:50].values('time', 'sip', 'dip', 'sport', 'dport', 'protocol', 'pkts', 'bytes', 'duration', 'labelOfService', 'labelOfAnomaly')
        result = list(flows_fea)
        for d in result:
            d['sip'] = str(ipaddress.ip_address(d['sip']))
            d['dip'] = str(ipaddress.ip_address(d['dip']))
        # flows_fea = serializers.serialize("json", flows_fea)
        
        return HttpResponse(json.dumps({'status': 'success', 'result':result}), content_type='application/json')
    elif request.method == 'POST':
        try:
            rb = json.loads(request.body)
            selectIP = rb['ip'] if 'ip' in rb.keys() else None
            selectTimeStart = rb['time_start'] if 'time_start' in rb.keys() else None
            selectTimeEnd = rb['time_end'] if 'time_end' in rb.keys() else None

            result = None
            if selectIP:
                # IP划分
                selectIP = int(ipaddress.ip_address(selectIP))
                result = Flowtables.objects.filter(Q(sip=selectIP) | Q(dip=selectIP))
            if selectTimeStart and selectTimeEnd:
                # 时间划分
                TS_stamp = int(time.mktime(time.strptime(selectTimeStart, '%Y-%m-%d %H:%M:%S')))
                TE_stamp = int(time.mktime(time.strptime(selectTimeEnd, '%Y-%m-%d %H:%M:%S')))
                # result = Flowtables.objects.filter(time__gt = TS_stamp).filter(time__lt = TE_stamp)
                if result:
                    result = result.filter(time__range = (TS_stamp, TE_stamp))
                else:
                    result = Flowtables.objects.filter(time__range = (TS_stamp, TE_stamp))
            # print(len(result))
            result = list(result.values('time', 'sip', 'dip', 'sport', 'dport', 'protocol', 'pkts', 'bytes', 'duration', 'labelOfService', 'labelOfAnomaly'))
            return HttpResponse(json.dumps({'status': 'success', 'result':result}), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')

# pcap/pcapng 文件上传
def upload_files(request):
    if request.method == 'POST':
        label = request.POST['label']
        files = request.FILES.getlist('files')

        result = []
        if len(files) > 0:
            rootDir = os.path.join('./classify/dataset/pcaps/', label)
            # 如果没有子目录, 新建
            if not os.path.exists(rootDir):
                os.mkdir(rootDir)
            for myfile in files:
                type = myfile.name.split('.')[-1]
                # 支持pcap/pcapng两种文件
                if type != 'pcap' and type != 'pcapng':
                    return HttpResponse(json.dumps({'status': 'fail', 'err': "file type can only be 'pcap' or 'pcapng'. "}))
                try:
                    # 如果文件名存在, 当前文件改为"xxx(1).csv"
                    dstDir = os.path.join(rootDir, myfile.name)
                    while(os.path.exists(dstDir)):
                        dstDir = os.path.join(dstDir.rsplit('.', 1)[0] + '(1).' + type)
                    
                    dstFile = open(dstDir,'wb+')    # 打开特定的文件进行二进制的写操作  
                    for chunk in myfile.chunks():      # 分块写入文件  
                        dstFile.write(chunk)
                    dstFile.close()
                    result.append(myfile.name)
                except Exception as e:
                    return HttpResponse({'status': 'fail', 'err': str(e)})
            
            return HttpResponse(json.dumps({'status': 'success', 'result':result}), content_type='application/json')

    return HttpResponse(json.dumps({'status': 'fail', 'err': "Request Method err, or no file to upload"}))


# 数据库选取数据 进行业务分类预测
def model_pred_mysql(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')
    try:
        # 参数读取
        rb = json.loads(request.body)
        method = rb['method'] # classic / lstm / united
        threshold = float(rb['threshold']) # 0.5
        
        selectIP = rb['ip'] if 'ip' in rb.keys() else None
        selectTimeStart = rb['time_start'] if 'time_start' in rb.keys() else None
        selectTimeEnd = rb['time_end'] if 'time_end' in rb.keys() else None
        
        # 数据库读取+过滤
        pred_data = None
        # pred_data = Flowtables.objects.filter(Q(sport = 443) | Q(dport = 443))
        # IP划分
        if selectIP:
            # print('开始ip筛选...')
            selectIP = int(ipaddress.ip_address(selectIP))
            pred_data = Flowtables.objects.filter(Q(sip=selectIP) | Q(dip=selectIP))
            if len(pred_data) == 0:
                raise Exception("IP地址不存在")
        # 时间划分
        if selectTimeStart and selectTimeEnd:
            
            TS_stamp = int(time.mktime(time.strptime(selectTimeStart, '%Y-%m-%d %H:%M:%S')))
            TE_stamp = int(time.mktime(time.strptime(selectTimeEnd, '%Y-%m-%d %H:%M:%S')))
            if pred_data:
                # print('开始时间筛选...')
                pred_data = pred_data.filter(time__range = (TS_stamp, TE_stamp))
            else:
                pred_data = Flowtables.objects.filter(time__range = (TS_stamp, TE_stamp))

        # 选择 labelOfService = None 的数据
        if pred_data:
            # print('开始筛选未分类数据...')
            pred_data = pred_data.filter(labelOfService = None)
        else:
            pred_data = Flowtables.objects.filter(labelOfService = None)

        # 选 n 条数据进行预测
        pred_data = pred_data[:min(random.randint(2000, 50000), pred_data.count())]
        
        classic_data = None
        lstm_data = None
        if method == 'classic' or method == 'united':
            classic_data = list(pred_data.values_list('sip', 'dip', 'sport', 'dport', 'protocol', 'pkts', 'bytes', 'duration'))
        if method == 'lstm' or method == 'united':
            lstm_data = list(pred_data.values_list('pdu1', 'pdu2', 'pdu3', 'pdu4', 'pdu5', 'pdu6', 'pdu7', 'pdu8', 'pdu9', 'pdu10', 
                                                'pdu11', 'pdu12', 'pdu13', 'pdu14', 'pdu15', 'pdu16', 'pdu17', 'pdu18', 'pdu19', 'pdu20', 
                                                'pdu21', 'pdu22', 'pdu23', 'pdu24'))
        
        # 模型选择
        model_dir = './classify/weights'
        if method == 'lstm':
            class_dict = getClassInfo(os.path.join(model_dir, 'lstm_ClassesInfo.txt'))
        else:
            class_dict = getClassInfo(os.path.join(model_dir, 'classic_ClassesInfo.txt'))
        
        print('构建分类模型...')
        pred_model = None
        if method == 'classic':
            # print(len(classic_data))
            if len(classic_data) == 0:
                raise Exception("数据为空")
            pred_model = Classic_Pred_MySQL(classic_data, model_dir, threshold, class_dict)
        elif method == 'lstm':
            if len(lstm_data) == 0:
                raise Exception("数据为空")
            pred_model = LSTM_Pred_MySQL(lstm_data, model_dir, threshold, class_dict)
        elif method == 'united':
            if len(classic_data) == 0 or len(lstm_data) == 0:
                raise Exception("数据为空")
            pred_model = United_Pred_MySQL(classic_data, lstm_data, model_dir, threshold, class_dict)
        
        result_json = pred_model.pred()
        
        class_dict[len(class_dict)] = 'Unknow'
        # print(class_dict)
        # 统计信息
        label_counter = dict()
        label_avg_prob = dict()
        
        print('更新数据库...')
        # tmpDict = dict()
        # for cla in class_dict.keys():
        #     tmpDict[cla] = []
        for data, res, prod in zip(pred_data, result_json['pred'], result_json['prob']):
            # 更新结果到数据库
            # data.labelOfService = res
            # data.save(force_update=True, update_fields=['labelOfService'])
            # print(data.sip, data.dip, data.sport, data.dport, data.labelOfService)
            # tmpDict[res].append(data)
            # 统计结果信息
            label_counter[class_dict[res]] = label_counter[class_dict[res]] + 1 if class_dict[res] in label_counter.keys() else 1
            label_avg_prob[class_dict[res]] = label_avg_prob[class_dict[res]] + prod if class_dict[res] in label_avg_prob.keys() else prod
        # print('更新数据库...')
        # for k,v in tmpDict.items():
        #     v.update({'labelOfService': k})


        # 计算各个类的平均置信度
        for key in label_avg_prob.keys():
            label_avg_prob[key] = label_avg_prob[key] / label_counter[key]
        
        return HttpResponse(json.dumps({'status': 'success', 'result': {'time': result_json['time'], 'num': len(pred_data), 'label_count':label_counter, 'label_avg_prod':label_avg_prob}}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')