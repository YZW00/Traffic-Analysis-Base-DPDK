from django.db import models, connection
from django.conf import settings
import os
import numpy as np
from picklefield.fields import PickledObjectField
import ipaddress, time
from django.db.models import Q
from django.db.models import Sum, Avg, Max, Min
import func_timeout
from func_timeout import func_set_timeout
from globalConf import *

# dpdk采集的流量特征表
class Flowtables(models.Model):
    time = models.PositiveBigIntegerField(blank=True, primary_key=True) # 
    sip = models.PositiveIntegerField(blank=True, null=True)
    dip = models.PositiveIntegerField(blank=True, null=True)
    sport = models.PositiveSmallIntegerField(blank=True, null=True)
    dport = models.PositiveSmallIntegerField(blank=True, null=True)
    protocol = models.PositiveIntegerField(blank=True, null=True)
    pkts = models.PositiveIntegerField(blank=True, null=True)
    bytes = models.PositiveIntegerField(blank=True, null=True)
    duration = models.PositiveIntegerField(blank=True, null=True)
    labelOfService = models.PositiveIntegerField(blank=True, null=True)  # Field name made lowercase.
    labelOfAnomaly = models.IntegerField(blank=True, null=True)  # Field name made lowercase.
    pdu1 = models.PositiveSmallIntegerField(db_column='PDU1', blank=True, null=True)  # Field name made lowercase.
    pdu2 = models.PositiveSmallIntegerField(db_column='PDU2', blank=True, null=True)  # Field name made lowercase.
    pdu3 = models.PositiveSmallIntegerField(db_column='PDU3', blank=True, null=True)  # Field name made lowercase.
    pdu4 = models.PositiveSmallIntegerField(db_column='PDU4', blank=True, null=True)  # Field name made lowercase.
    pdu5 = models.PositiveSmallIntegerField(db_column='PDU5', blank=True, null=True)  # Field name made lowercase.
    pdu6 = models.PositiveSmallIntegerField(db_column='PDU6', blank=True, null=True)  # Field name made lowercase.
    pdu7 = models.PositiveSmallIntegerField(db_column='PDU7', blank=True, null=True)  # Field name made lowercase.
    pdu8 = models.PositiveSmallIntegerField(db_column='PDU8', blank=True, null=True)  # Field name made lowercase.
    pdu9 = models.PositiveSmallIntegerField(db_column='PDU9', blank=True, null=True)  # Field name made lowercase.
    pdu10 = models.PositiveSmallIntegerField(db_column='PDU10', blank=True, null=True)  # Field name made lowercase.
    pdu11 = models.PositiveSmallIntegerField(db_column='PDU11', blank=True, null=True)  # Field name made lowercase.
    pdu12 = models.PositiveSmallIntegerField(db_column='PDU12', blank=True, null=True)  # Field name made lowercase.
    pdu13 = models.PositiveSmallIntegerField(db_column='PDU13', blank=True, null=True)  # Field name made lowercase.
    pdu14 = models.PositiveSmallIntegerField(db_column='PDU14', blank=True, null=True)  # Field name made lowercase.
    pdu15 = models.PositiveSmallIntegerField(db_column='PDU15', blank=True, null=True)  # Field name made lowercase.
    pdu16 = models.PositiveSmallIntegerField(db_column='PDU16', blank=True, null=True)  # Field name made lowercase.
    pdu17 = models.PositiveSmallIntegerField(db_column='PDU17', blank=True, null=True)  # Field name made lowercase.
    pdu18 = models.PositiveSmallIntegerField(db_column='PDU18', blank=True, null=True)  # Field name made lowercase.
    pdu19 = models.PositiveSmallIntegerField(db_column='PDU19', blank=True, null=True)  # Field name made lowercase.
    pdu20 = models.PositiveSmallIntegerField(db_column='PDU20', blank=True, null=True)  # Field name made lowercase.
    pdu21 = models.PositiveSmallIntegerField(db_column='PDU21', blank=True, null=True)  # Field name made lowercase.
    pdu22 = models.PositiveSmallIntegerField(db_column='PDU22', blank=True, null=True)  # Field name made lowercase.
    pdu23 = models.PositiveSmallIntegerField(db_column='PDU23', blank=True, null=True)  # Field name made lowercase.
    pdu24 = models.PositiveSmallIntegerField(db_column='PDU24', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FlowTables'
        # unique_together = ("sip", "dip", "sport", "dport", "protocol")
        # constraints = [
        #     models.UniqueConstraint(fields=["time", "sip", "dip", "sport", "dport", "protocol"], name='id')
        # ]

class IPImage(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.PositiveBigIntegerField(blank=True, null=True)
    ip = models.PositiveIntegerField(blank=True, null=True)
    sumPkts = models.PositiveIntegerField(blank=True, null=True)
    sumBytes = models.PositiveIntegerField(blank=True, null=True)
    avgDuration = models.PositiveIntegerField(blank=True, null=True)
    label_num = PickledObjectField(blank=True, null=True)

class AnomalyRecord(models.Model):
    timeStamp = models.PositiveBigIntegerField(primary_key = True)
    targetIP = models.PositiveIntegerField()
    anomalyType = PickledObjectField(blank=True, null=True)
    anomalyInfo = PickledObjectField(blank=True, null=True)

def findAnomalyData(data):
    # 将上、下限设为3倍标准差
    data_std = np.std(data) 
    data_mean = np.mean(data) 
    anomaly_cut_off = data_std * 3
    lower_limit = data_mean - anomaly_cut_off 
    upper_limit = data_mean + anomaly_cut_off
    
    anomaly_index = []
    for (i, outlier) in enumerate(data):
        if outlier > upper_limit or outlier < lower_limit:
            anomaly_index.append(i)
    return anomaly_index

anomaly_dict = {
    0: "流量报文数异常",
    1: "流量数据量异常", 
    2: "流量时间异常",
    3: "流业务类型异常",
    4: "业务流分布异常"
}

# 自动更新IP画像
@func_set_timeout(IP_image_update_cycle)
def auto_update_image():
    try:
        # 删除旧数据
        # flowCount = Flowtables.objects.count()
        # Flowtables.objects.filter(time__in = list(Flowtables.objects.order_by('time').values_list('pk', flat=True)[:int(flowCount * delete_flow_ratio)])).delete()
        # imageCount = IPImage.objects.count()
        # IPImage.objects.filter(id__in = list(IPImage.objects.order_by('time').values_list('pk', flat=True)[:int(imageCount * delete_image_ratio)])).delete()
        # print('{} [info]: 成功清除过期数据'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
        print('{} 开始构建新画像'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
        # 构建新Image
        selectIPs = set(list(Flowtables.objects.values_list('sip')))
        tmp_IPs = set([ip[0] for ip in selectIPs])
        int_selectIPs = tmp_IPs
        # 时间片尺寸
        hour_win = 2
        second_win = 3600 * hour_win
        startTime = IPImage.objects.aggregate(Max('time'))['time__max']
        if startTime:
            startTime += 1
        
        if not selectIPs:
            print("{} [Error]: 没有找到 IP 信息".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
            return
        
        for int_ip in int_selectIPs:
            print('{} [info]: 正在构建{}画像:'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), str(ipaddress.ip_address(int_ip))) , flush=True)
            
            # 先划分IP
            ip_flows = Flowtables.objects.filter(Q(sip=int_ip) | Q(dip=int_ip))
            # 再切分时间片
            if not startTime:
                startTime = ip_flows.aggregate(Min('time'))['time__min']
            if not startTime:
                return None
            endTime = ip_flows.aggregate(Max('time'))['time__max']
            
            curTime = startTime

            # [Error]: '<' not supported between instances of 'int' and 'NoneType' 需调试
            if not curTime or not endTime:
                continue
            while curTime < endTime:
                print('{} [info]: 新增条目'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
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
        
        print("{} [info]: 本轮画像构建完成".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    except Exception as e:
        print("{} [Error]: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), e), flush=True)

def run_auto_update_image():
    try:
        auto_update_image()
    except func_timeout.exceptions.FunctionTimedOut as e:
        print('{} [Warning]: 本轮更新超时, 未全部完成'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    except Exception as e:
        print('{} [Error]: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), str(e)), flush=True)


# 自动清除过时数据
def auto_delete():
    # mysql单表记录上限设置为500万条
    flowCount = Flowtables.objects.count()
    if flowCount > 5000000:
        try:
            # 删除 Flowtables 旧数据
            deleteNum = int(flowCount * delete_flow_ratio)
            # Flowtables.objects.all()[:deleteNum].delete()
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM FlowTables LIMIT {}".format(deleteNum))
                # resInfo = cursor.fetchall()
            print('{} [info]: 成功清除 FlowTables 数据 {} 条'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), deleteNum), flush=True)
        except Exception as e:
            print("{} [Error]: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), e), flush=True)
    # else:
    #     print('{} [info]: FlowTables 数据量正常: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), flowCount), flush=True)
    
    # 删除 IPImage 旧数据
    imageCount = IPImage.objects.count()
    if imageCount > 5000000:
        try:
             # 删除 Flowtables 旧数据
            deleteNum = int(imageCount * delete_image_ratio)
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM detect_ipimage order by time LIMIT {}".format(deleteNum))
            
            # IPImage.objects.filter(id__in = list(IPImage.objects.order_by('time').values_list('pk', flat=True)[:int(imageCount * delete_image_ratio)])).delete()
            print('{} [info]: 成功清除 IPImage 数据 {} 条'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), deleteNum), flush=True)
            
        except Exception as e:
            print("{} [Error]: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), e), flush=True)

# 自动清除过时pcap
def auto_delete_pcap():
    pcapDir = '/data/pcaps'
    pcapSize, pcapCnt = 0, 0
    try:
        for root, dirs, files in os.walk(pcapDir):
            for file in files:
                if file.endswith('.pcap'):
                    pcapCnt += 1
                    pcapSize += os.path.getsize(os.path.join(root, file))
        print('pcapSize:{:.2f} GB'.format(pcapSize / 1024 / 1024 / 1024))
        pcapDelet = int(pcapCnt * pcap_delete_ratio)
        if pcapSize >= 30 * 1024 * 1024 * 1024:
            for root, dirs, files in os.walk(pcapDir):
                if pcapDelet <= 0:
                        break
                for file in files:
                    if pcapDelet <= 0:
                        break
                    if file.endswith('.pcap'):
                        pcapDelet -= 1
                        os.remove(os.path.join(root, file))
            print('{} [info]: 成功清除 pcap 数据'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    except Exception as e:
        print("{} [Error]: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), e), flush=True)


def test():
    count = 0
    while(True):
        print(count, flush=True)
        time.sleep(70)
        count += 1