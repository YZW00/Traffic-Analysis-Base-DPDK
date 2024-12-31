'''
功能:基于长度序列特征预测分类模型LS-LSTM, 读取pkl权重, 后对读入数据进行预测
参数:
    dataset_dir: 待预测的csv文件目录
    model_dir: 模型权重的保存目录, 类别字典lstm_ClassesInfo.txt
输出:model_dir目录下生成pkl文件
运行示例: python3 lstmNet_pred.py ../dataset/Features/tcp ../weights 0.5
'''
import torch
from torch import nn
from torch.utils.data import DataLoader
import time
import numpy as np
import argparse
import os
from .RNN import RNN
from .getClassInfo import getClassInfo

class LSTM_Pred:
    def __init__(self, dataset_dir, model_dir, threshold, class_dict):
        self.dataset_dir = dataset_dir
        self.model_dir = model_dir
        self.threshold = threshold
        self.batch_size = 600
        self.max_payload_length = 66000
        self.class_dict = class_dict
        self.num_classes = len(class_dict)
        self.result = dict()

    def load_dataset(self):
        X_test = np.loadtxt(os.path.join(self.dataset_dir, 'lenSeq.csv'), delimiter = ',')
        # y_test = np.loadtxt(os.path.join(dataset_dir,"label.csv"), delimiter = ',')
        
        dataset_test = torch.tensor(X_test, dtype = torch.float32)
        return dataset_test
        
    def tmp_final_evaluate(self, model, dataset_test, device):
        # 数据loader
        model = model.to(device)
        data_loader = DataLoader(dataset_test, batch_size = self.batch_size, shuffle=False)
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
            time_stamp = time.time()
        
        y_pred_label = []
        for (pred, prob) in zip(y_pred, y_prob):
            if prob < self.threshold:
                y_pred_label.append('未知')
            else:
                y_pred_label.append(self.class_dict[pred])
        # print("预测：{}, 置信度:{}, 标签：{}".format(y_pred_label,y_prob, y_true_label))

        # saveDir = '.'
        # with open(os.path.join(saveDir,'lenSeq_pred.txt'), 'w') as f:
        #     for pred,prob in zip(y_pred_label, y_prob):
        #         f.write("%s\t%f\n" % (pred,prob))
        self.result['pred'] = list(y_pred_label)
        self.result['prob'] = list(y_prob)
        
        return time_stamp
    
    def pred(self):
        device = None
        if torch.cuda.is_available():
           device = torch.device('cuda',0)
           print('使用GPU')
        else:
           print('使用CPU')
        try:
            print('开始预测...')
            start = time.time()
            dataset_test = self.load_dataset()
            model = RNN(self.max_payload_length, self.num_classes)
            model.load_state_dict(torch.load(os.path.join(self.model_dir, "lstm_model.pkl")))
            end = self.tmp_final_evaluate(model, dataset_test, device)
            print('预测结束...耗时:{:.2f}'.format(end-start))
            self.result['time'] = end-start
            self.result['status'] = "success"
            return self.result
        except Exception as e:
            return {'status':'fail', 'error':str(e)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='长度序列分类模型分类所需参数')
    parser.add_argument('dataset_dir')
    parser.add_argument('model_dir')
    parser.add_argument('threshold', type=float)

    args = parser.parse_args()
    # 待预测csv、标签csv、ClassesInfo所在目录
    dataset_dir = args.dataset_dir
    # 模型文件目录
    model_dir = args.model_dir
    # 置信度阈值, 低于该阈值的样本将被判定为未知类别
    threshold = args.threshold
    
    class_dict = getClassInfo(os.path.join(model_dir, "lstm_ClassesInfo.txt"))
    lstm_model = LSTM_Pred(dataset_dir, model_dir, threshold, class_dict)
    result = lstm_model.pred()
    print(result)
    