from django.db import models
from .utils.united_pred_mysql import United_Pred_MySQL
from .utils.lstmNet_pred_mysql import LSTM_Pred_MySQL
from .utils.getClassInfo import getClassInfo
import time, func_timeout, os
from django.db.models import Q
from func_timeout import func_set_timeout
from pathlib import Path

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
        # unique_together = ( "sip", "dip", "sport", "dport", "protocol")

@func_set_timeout(3600*3)
def auto_model_pred_mysql():
    # try:
    print('{} [info]: 本轮业务类别预测开始'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    # 参数读取
    threshold = 0.55
    # 选择 labelOfService = None 的数据
    pred_data = Flowtables.objects.filter(labelOfService = None)#.filter(Q(sip=321388552) | Q(dip=321388552))
    pred_data = pred_data.exclude(pdu1 = None).exclude(pdu2 = None).exclude(pdu3 = None).exclude(pdu4 = None).exclude(pdu5 = None).exclude(pdu6 = None) \
                        .exclude(pdu7 = None).exclude(pdu8 = None).exclude(pdu9 = None).exclude(pdu10 = None).exclude(pdu11 = None).exclude(pdu12 = None) \
                        .exclude(pdu13 = None).exclude(pdu14 = None).exclude(pdu15 = None).exclude(pdu16 = None).exclude(pdu17 = None).exclude(pdu18 = None) \
                        .exclude(pdu19 = None).exclude(pdu20 = None).exclude(pdu21 = None).exclude(pdu22 = None).exclude(pdu23 = None).exclude(pdu24 = None)
    
    # classic_data = list(pred_data.values_list('sip', 'dip', 'sport', 'dport', 'protocol', 'pkts', 'bytes', 'duration'))
    lstm_data = list(pred_data.values_list('pdu1', 'pdu2', 'pdu3', 'pdu4', 'pdu5', 'pdu6', 'pdu7', 'pdu8', 'pdu9', 'pdu10', 
                                            'pdu11', 'pdu12', 'pdu13', 'pdu14', 'pdu15', 'pdu16', 'pdu17', 'pdu18', 'pdu19', 'pdu20', 
                                            'pdu21', 'pdu22', 'pdu23', 'pdu24'))
    
    # cur_index = 0
    # while(cur_index < pred_data.count()):
    #     cur_data = pred_data[cur_index:min(cur_index+2000, pred_data.count())]
    
    print(Path(__file__).resolve().parent)
    
    # 模型选择 StateGridTraffic/
    model_dir = os.path.join(Path(__file__).resolve().parent, 'weights') # ./StateGrid/StateGridTraffic/weights
    class_dict = getClassInfo(os.path.join(Path(__file__).resolve().parent, 'weights/lstm_ClassesInfo.txt'))
    
    if os.getcwd().rsplit('/',1)[1] == 'StateGridTraffic':
        model_dir = './classify/weights'
        class_dict = getClassInfo('./classify/weights/lstm_ClassesInfo.txt')
    
    print('{} [info]: 构建分类模型'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    # pred_model = United_Pred_MySQL(classic_data, lstm_data, model_dir, threshold, class_dict)
    pred_model = LSTM_Pred_MySQL(lstm_data, model_dir, threshold, class_dict)
    print('{} [info]: 开始预测'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    result_json = pred_model.pred()
    class_dict[len(class_dict)] = 'Unknow'

    if result_json['status'] == 'fail':
        print('err:',result_json['error'])

    print('{} [info]: 预测完成. {} 开始更新数据库'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), len(result_json['pred'])), flush=True)
        
    # cur_index += 2000
    for data, res in zip(pred_data, result_json['pred']):
        # 更新结果到数据库
        data.labelOfService = res
        data.save(force_update=True, update_fields=['labelOfService'])
        # target_data = Flowtables.objects.get(time = data.time, sip = data.sip, dip = data.dip, sport = data.sport, dport = data.dport)
        # target_data.labelOfService = res
        # target_data.save(force_update=True)
        print('{} [info]: 更新条目业务标签 {} {} {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), data.time, data.sip, data.labelOfService), flush=True)
        
    print('{} [info]: 本轮更新全部完成'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), flush=True)
    # except Exception as e:
    #     print('{} [Error]: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), str(e)), flush=True)

def run_auto_model_pred():
    try:
        auto_model_pred_mysql()
    except func_timeout.exceptions.FunctionTimedOut as e:
        print('{} [Warning]: 本轮更新超时, 未全部完成'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    except Exception as e:
        print('{} [Error]: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), str(e)), flush=True)