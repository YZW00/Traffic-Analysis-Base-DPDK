'''
功能:基于长度序列特征预测分类模型LS-LSTM, 读取pkl权重, 后对读入数据进行预测
参数:
    dataset_dir: 待预测的csv文件目录
    model_dir: 模型权重的保存目录, 类别字典lstm_ClassesInfo.txt
输出:model_dir目录下生成pkl文件
运行示例: python3 united_pred.py ../dataset/Features/tcp ../weights 0.5
'''

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler # 归一化
import torch
from torch import nn
from torch.utils.data import DataLoader
import time, os
import numpy as np
import argparse
import ipaddress
from threading import Thread
from sklearn.metrics import accuracy_score, classification_report
from .getClassInfo import getClassInfo
from .RNN import RNN


class MyThread(Thread):
    def run(self):
        self.result = self._target(*self._args, **self._kwargs)
    
    def get_result(self):
        return self.result

class United_Pred:
    def __init__(self, dataset_dir, model_dir, threshold, class_dict):
        self.dataset_dir = dataset_dir
        self.model_dir = model_dir
        self.threshold = threshold
        self.class_dict = class_dict
        self.num_classes = len(class_dict)
        self.batch_size = 600
        self.max_payload_length = 66000
        self.result = dict()

    def load_dataset(self):
        statitical_test = pd.read_csv(os.path.join(self.dataset_dir, 'statistical.csv'), index_col=False, header=None)
        # 将IP地址转换为整数
        statitical_test[0] = statitical_test[0].apply(lambda x: int(ipaddress.ip_address(x)))
        statitical_test[1] = statitical_test[1].apply(lambda x: int(ipaddress.ip_address(x)))
        # 归一化操作
        scaler = StandardScaler()
        statitical_test = scaler.fit_transform(statitical_test.values)
        # 读取长度序列
        lenSeq_test = np.loadtxt(os.path.join(self.dataset_dir, 'lenSeq.csv'), delimiter = ',')
        lenSeq_test = torch.tensor(lenSeq_test, dtype = torch.float32)
        return statitical_test, lenSeq_test

    # 统计特征分类模型
    def statistical_pred(self, model_dir, statitical_test):
        model = joblib.load(os.path.join(model_dir, 'classic_model.m'))
        y_pred_prob = model.predict_proba(statitical_test)
        my_pred = np.array([np.argmax(pred) for pred in y_pred_prob])
        prob_pred = np.array([np.max(pred) for pred in y_pred_prob])

        # 若预测概率小于阈值,则预测为-1(未知类别)
        # my_pred[prob_pred < 0.5] = -1
        print('classic预测完成...')
        return my_pred, prob_pred

    # 长度序列分类模型
    def lenSeq_pred(self, model_dir, lenSeq_test):
        device = None
        if torch.cuda.is_available():
            device = torch.device('cuda',0)
            print('使用GPU')
        else:
            print('使用CPU')
        # 加载模型
        model = RNN(self.max_payload_length, self.num_classes)
        model.load_state_dict(torch.load(os.path.join(model_dir, "lstm_model.pkl")))

        # 数据loader
        model = model.to(device)
        data_loader = DataLoader(lenSeq_test, batch_size = self.batch_size, shuffle=False)
        y_pred = np.array([],dtype=int)
        y_prob = np.array([],dtype=float)
        # y_true_label = np.array([])
        with torch.no_grad():
            for i, X in enumerate(data_loader):
                # y_true_label = np.hstack((y_true_label, y.numpy()))
                X = torch.from_numpy(np.array(X))
                tmp = model(X.long().to(device))
                y_pred = np.hstack((y_pred, tmp.argmax(dim = -1).cpu().numpy()))
                y_prob = np.hstack((y_prob, tmp.max(dim = -1).values.cpu().numpy()))
        print('lenSeq预测完成...')
        return y_pred, y_prob

    def pred(self):
        # 加载数据
        statitical_test, lenSeq_test = self.load_dataset()
        print("数据加载完成...")
        
        start = time.time()
        classicThread = MyThread(target = self.statistical_pred, args = (self.model_dir, statitical_test))
        lenSeqThread = MyThread(target = self.lenSeq_pred, args = (self.model_dir, lenSeq_test))
        classicThread.setDaemon(True)
        lenSeqThread.setDaemon(True)
        classicThread.start()
        lenSeqThread.start()
        classicThread.join(30) # 子线程30s超时
        lenSeqThread.join(30) # 子线程30s超时
        
        duration = time.time() - start
        print("预测结束...耗时:{:.2f}".format(duration))

        try:
            # 统计特征分类模型预测结果
            classic_pred, classic_prob = classicThread.get_result()
            # 长度序列分类模型预测结果
            lenSeq_pred, lenSeq_prob = lenSeqThread.get_result()

            # 联合预测结果
            lenSeq_pred[classic_prob > lenSeq_prob] = classic_pred[classic_prob > lenSeq_prob]
            lenSeq_prob[classic_prob > lenSeq_prob] = classic_prob[classic_prob > lenSeq_prob]
            # 预测结果转换为类别名称
            y_pred_label = np.array([self.class_dict[pred] for pred in lenSeq_pred])
            y_pred_label[lenSeq_prob < self.threshold] = '未知'

            # saveDir = '.'
            # with open(os.path.join(saveDir,'united_pred.txt'), 'w') as f:
            #     for pred,prob in zip(y_pred_label, lenSeq_prob):
            #         f.write("%s\t%f\n" % (pred,prob))

            self.result['pred'] = y_pred_label.tolist()
            self.result['prob'] = lenSeq_prob.tolist()
            self.result['time'] = duration
            self.result['status'] = "success"
            return self.result
        except Exception as e:
            return {'status': 'fail', 'error':str(e)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='统计特征分类模型分类所需参数')
    parser.add_argument('dataset_dir')
    parser.add_argument('model_dir')
    parser.add_argument('threshold', type=float)

    args = parser.parse_args()
    # 待预测的特征csv文件目录
    dataset_dir = args.dataset_dir
    # 模型文件目录
    model_dir = args.model_dir
    # 置信度阈值: classic模型预测结果未达到的数据，使用lstm模型再进行预测。
    threshold = args.threshold # 0.5

    class_dict = getClassInfo(os.path.join(model_dir, "classic_ClassesInfo.txt"))
    united_model = United_Pred(dataset_dir, model_dir, threshold, class_dict)
    result = united_model.pred()
    print(result)