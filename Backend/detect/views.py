from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Sum, Avg, Max, Min
from .models import Flowtables, IPImage, findAnomalyData, AnomalyRecord, anomaly_dict
from .utils.getClassInfo import getClassInfo
import json, time
import ipaddress
# Create your views here.

def index(request):
    return HttpResponse("Hello, You're at the Anomaly Detect index.")

# 获取IP流量画像信息
def get_ip_image(request):
    if request.method == 'POST':
        try:
            rb = json.loads(request.body)
            selectIPs = rb['IPlist']
            int_selectIPs = [int(ipaddress.ip_address(ip)) for ip in selectIPs]
            result = dict()
            for ip, int_ip in zip(selectIPs, int_selectIPs):
                result[ip] = {}
                ip_flows = Flowtables.objects.filter(Q(sip=int_ip) | Q(dip=int_ip))
                result[ip]['flow_num'] = len(ip_flows)
                result[ip]['avg_duration'] = ip_flows.aggregate(Avg('duration'))['duration__avg']
                result[ip]['sum_bytes'] = ip_flows.aggregate(Sum('bytes'))['bytes__sum']
                tmp = list(ip_flows.values('sip', 'dip'))
                ip_list = []
                for v in tmp:
                    ip_list.extend(v.values())
                ip_list = list(set(ip_list))
                ip_list.remove(int_ip)
                relate_ip = [str(ipaddress.ip_address(tmp_ip)) for tmp_ip in ip_list]

                result[ip]['relate_ip'] = dict()
                for rp, int_rip in zip(relate_ip, ip_list):
                    result[ip]['relate_ip'][rp] = dict()
                    relate_flows = ip_flows.filter(Q(sip=int_rip) | Q(dip=int_rip))
                    result[ip]['relate_ip'][rp]['flow_num'] = len(relate_flows)
                    result[ip]['relate_ip'][rp]['avg_duration'] = relate_flows.aggregate(Avg('duration'))['duration__avg']
                    result[ip]['relate_ip'][rp]['sum_bytes'] = relate_flows.aggregate(Sum('bytes'))['bytes__sum']
                
            return HttpResponse(json.dumps({'status': 'success', 'result':result}), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')

# 生成IP流量画像
def gen_IP_image(request):
    try:
        int_selectIPs = None
        rb = None
        selectIPs = None
        hour_win = 3
        if request.method == 'POST':
            rb = json.loads(request.body)
            selectIPs = rb['IPlist'] if 'IPlist' in rb.keys() else None
            hour_win = float(rb['time_window']) if 'time_window' in rb.keys() else 3
        if selectIPs:
            int_selectIPs = [int(ipaddress.ip_address(ip)) for ip in selectIPs]
            image_ip_set = set(list(IPImage.objects.values_list('ip', flat=True)))
            exist_flag = True
            for int_ip in int_selectIPs:
                if int_ip not in image_ip_set:
                    exist_flag = False
                else:
                    int_selectIPs.remove(int_ip)
            if exist_flag:
                return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
        
        if not int_selectIPs:
            int_selectIPs = set(list(Flowtables.objects.values_list('sip')))
            tmp_IPs = set([ip[0] for ip in int_selectIPs])
            int_selectIPs = tmp_IPs
        # 时间片尺寸
        second_win = 3600 * hour_win
        
        if not int_selectIPs:
            return HttpResponse(json.dumps({'status': 'fail', 'err': 'No IP found in database'}), content_type='application/json')
        
        for int_ip in int_selectIPs:
            print('int_ip:', int_ip)
            # 先划分IP
            ip_flows = Flowtables.objects.filter(Q(sip=int_ip) | Q(dip=int_ip))
            if ip_flows.count() == 0:
                continue
            # 再切分时间片
            startTime = None
            exist_ip_image = IPImage.objects.filter(ip = int_ip)
            if exist_ip_image.count() > 0:
                last_time = exist_ip_image.aggregate(Max('time'))['time__max']
                ip_flows = ip_flows.filter(time__gt = last_time)
            
            startTime = ip_flows.aggregate(Min('time'))['time__min']
            print('startTime', startTime)
            if not startTime:
                continue
            endTime = ip_flows.aggregate(Max('time'))['time__max'] - second_win
            
            curTime = startTime
            while curTime < endTime:
                print('curTime:',curTime)
                ip_flows_win = ip_flows.filter(time__range = (curTime, curTime + second_win))
                sumBytes = ip_flows_win.aggregate(Sum('bytes'))['bytes__sum']
                sumPkts = ip_flows_win.aggregate(Sum('pkts'))['pkts__sum']
                avgDuration = ip_flows_win.aggregate(Avg('pkts'))['pkts__avg']
                label_num = dict()
                labels = list(ip_flows_win.values_list('labelOfService'))
                labels = [lab[0] for lab in labels]
                tmpSet = set(labels)
                for item in tmpSet:
                    label_num.update({item:labels.count(item)})
                IPImage.objects.create(time = curTime, ip = int_ip, sumPkts = sumPkts, sumBytes = sumBytes, avgDuration = avgDuration, label_num = label_num)
                curTime += second_win
        
        return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')


# 展示IP流量画像
def show_IP_image(request):
    class_dict = getClassInfo('./classify/weights/lstm_ClassesInfo.txt')
    class_dict[len(class_dict)] = 'Unknow'
    result = None
    try:
        if request.method == 'POST':
            rb = json.loads(request.body)
            selectIP = rb['ip']
            int_selectIP = int(ipaddress.ip_address(selectIP))
            result = list(IPImage.objects.filter(ip = int_selectIP).values())
        else:
            result = list(IPImage.objects.values())
        
        for data in result:
            data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['time']))
            data['ip'] = str(ipaddress.ip_address(data['ip']))
            if data['label_num']:
                tmp_dict = {}
                for k in data['label_num'].keys():
                    if k in class_dict.keys():
                        tmp_dict[class_dict[k]] = data['label_num'][k]
                data['label_num'] = tmp_dict
        
            if not data['sumPkts']:
                data['sumPkts'] = 0
            if not data['sumBytes']:
                data['sumBytes'] = 0
            if not data['avgDuration']:
                data['avgDuration'] = 0
        
        return HttpResponse(json.dumps({'status': 'success', 'result':result}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')

# # 异常检测
def anomaly_detect(request):
    class_dict = getClassInfo('./classify/weights/lstm_ClassesInfo.txt')
    anomaly_count = 0

    try:
        # 选定ip 列表
        selectIPs = None
        print('IP过滤ing')
        if request.method == 'POST':
            rb = json.loads(request.body)
            selectIPs = rb['IPlist'] if 'IPlist' in rb.keys() else None

        if selectIPs == None:
            int_selectIPs = set(list(IPImage.objects.values_list('ip')))
            tmp_IPs = set([ip[0] for ip in int_selectIPs])
            int_selectIPs = tmp_IPs
        else:
            int_selectIPs = [int(ipaddress.ip_address(ip)) for ip in selectIPs]
        
        # 遍历选定IP
        for int_ip in int_selectIPs:
            # 建立异常记录条目
            anomalyType = []
            info = dict()
            # 获取IP画像数据
            ip_images = IPImage.objects.filter(ip = int_ip).order_by('time')
            time_list = []
            sumPkts_list = []
            sumBytes_list = []
            avgDuration_list = []
            label_rate = {}
            # print('IP:', str(ipaddress.ip_address(int_ip)), '获取画像ing')
            # 遍历IP画像
            for image in ip_images:
                time_list.append(image.time)
                sumPkts_list.append(image.sumPkts if image.sumPkts else 0)
                sumBytes_list.append(image.sumBytes if image.sumBytes else 0)
                avgDuration_list.append(image.avgDuration if image.avgDuration else 0)
                if image.label_num:
                    if len(class_dict) in image.label_num.keys():
                        anomalyType.append(3) # 业务类型异常
                        info['anomaly_flow'] = list(Flowtables.objects.filter(Q(sip = int_ip) | Q(dip = int_ip)).filter(time__range = (image.time, image.time + 3600))[:min(30, image.label_num[len(class_dict)])].values('time', 'sip', 'dip', 'sport', 'dport', 'protocol', 'pkts', 'bytes', 'duration'))
            # Pkts
            anomaly_index = findAnomalyData(sumPkts_list)
            if anomaly_index:
                anomalyType.append(0)
                info['anomaly_pkts'] = {'data':sumPkts_list, 'ano_index':anomaly_index}
            # Bytes
            anomaly_index = findAnomalyData(sumBytes_list)
            if anomaly_index:
                anomalyType.append(1)
                info['anomaly_bytes'] = {'data':sumBytes_list, 'ano_index':anomaly_index}
            # avg_duration
            anomaly_index = findAnomalyData(avgDuration_list)
            if anomaly_index:
                anomalyType.append(2)
                info['anomaly_duration'] = {'data':avgDuration_list, 'ano_index':anomaly_index}
            # 时间片 列表
            info['time_list'] = time_list
            if len(anomalyType) > 0:
                # print('IP:',str(ipaddress.ip_address(ip)) ,'生成异常记录')
                if AnomalyRecord.objects.filter(timeStamp = int(time.time())):
                    continue
                AnomalyRecord.objects.create(timeStamp = int(time.time()), targetIP = int_ip, anomalyType = anomalyType, anomalyInfo = info)
                anomaly_count += 1

        return HttpResponse(json.dumps({'status': 'success', 'anomaly_count':anomaly_count}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')

def show_anomaly(request):
    selectedIP = None
    if request.method == 'POST':
        rb = json.loads(request.body)
        selectedIP = int(ipaddress.ip_address(rb['ip']))
    try:
        if selectedIP:
            result_list = list(AnomalyRecord.objects.filter(targetIP = selectedIP).values('timeStamp', 'targetIP', 'anomalyType'))
        else:
            result_list = list(AnomalyRecord.objects.all().values('timeStamp', 'targetIP', 'anomalyType'))
        for result in result_list:
            result['timeStamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timeStamp']))
            result['targetIP'] = str(ipaddress.ip_address(result['targetIP']))
            anomaly_type = [anomaly_dict[at] for at in result['anomalyType']]
            result['anomalyType'] = anomaly_type

            # if 'anomaly_flow' in result['anomalyInfo'].keys():
            #     for v in result['anomalyInfo']['anomaly_flow']:
            #         v['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v['time']))
            #         v['sip'] = str(ipaddress.ip_address(v['sip']))
            #         v['dip'] = str(ipaddress.ip_address(v['dip']))
            # if 'time_list' in result['anomalyInfo'].keys():
            #     tmp_ts_list = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts)) for ts in result['anomalyInfo']['time_list']]
            #     result['anomalyInfo']['time_list'] = tmp_ts_list
        return HttpResponse(json.dumps({'status': 'success', 'result':result_list}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')

def show_anomaly_detail(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')
    try:
        rb = json.loads(request.body)
        strTime = rb['time']
        timeStamp = time.mktime(time.strptime(strTime, '%Y-%m-%d %H:%M:%S'))
        result = list(AnomalyRecord.objects.filter(timeStamp = timeStamp).values('anomalyInfo'))[0]
        if not result:
            return HttpResponse(json.dumps({'status': 'fail', 'err': 'No Record Found'}), content_type='application/json')
        result = result['anomalyInfo']
        if 'anomaly_flow' in result.keys():
            for v in result['anomaly_flow']:
                v['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v['time']))
                v['sip'] = str(ipaddress.ip_address(v['sip']))
                v['dip'] = str(ipaddress.ip_address(v['dip']))
        if 'time_list' in result.keys():
            tmp_ts_list = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts)) for ts in result['time_list']]
            result['time_list'] = tmp_ts_list

        return HttpResponse(json.dumps({'status': 'success', 'result':result}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')
