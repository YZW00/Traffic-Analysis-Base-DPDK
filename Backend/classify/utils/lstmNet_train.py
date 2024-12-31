'''
功能:基于长度序列特征训练分类模型,将模型权重保存为pkl文件
参数:
    dataset_dir: 待预测的csv文件目录,包含长度序列csv文件、标签csv文件、类别字典ClassesInfo.txt
    model_dir: 模型权重的保存目录，若没有则创建
输出:model_dir目录下生成pkl文件
运行示例: python3 lstmNet_train.py ../dataset/Features/tcp ../weights
'''
import torch
from torch import nn
from torch.optim import Adam
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import argparse
import shutil
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score
import os, time
from .getClassInfo import getClassInfo
from .RNN import RNN


class LSTM_Train:
    def __init__(self, dataset_dir, model_dir, class_dict):
        self.epochs = 200
        self.lr = 0.002
        self.batch_size = 800
        self.max_payload_length = 66000
        self.dataset_dir = dataset_dir
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        self.class_dict = class_dict
        self.num_classes = len(class_dict)
        self.class_name = class_dict.values()
        self.train_log = []
        shutil.copyfile(os.path.join(dataset_dir, "ClassesInfo.txt"), os.path.join(model_dir, "lstm_ClassesInfo.txt"))
        self.result = dict()
        
    def load_dataset(self, rate):
        dataset = np.loadtxt(os.path.join(self.dataset_dir,"lenSeq.csv"), delimiter = ',')
        labelset = np.loadtxt(os.path.join(self.dataset_dir,"label.csv"), delimiter = ',')

        X_train, X_test, y_train, y_test = train_test_split(dataset, labelset, test_size = rate, shuffle = True)

        dataset_train = TensorDataset(torch.tensor(X_train, dtype = torch.float32), torch.tensor(y_train, dtype = torch.int64))
        dataset_test = TensorDataset(torch.tensor(X_test, dtype = torch.float32), torch.tensor(y_test, dtype = torch.int64))

        return dataset_train, dataset_test

    def evaluate_accuracy(self, model, dataset, device):
        # 数据loader
        data_loader = DataLoader(dataset, batch_size = self.batch_size, shuffle=True)
        acc_sum, n = 0.0, 0
        with torch.no_grad():
            for i, (X, y) in enumerate(data_loader): 
                X = X.to(device)
                y = y.to(device)
                y_pred = model(X.long())
                acc_sum += (y_pred.argmax(dim=1) == y).float().sum().cpu().item()
                n += self.batch_size
        return acc_sum / n

    def final_evaluate(self, model, dataset_test, device):
        # 数据loader
        data_loader = DataLoader(dataset_test, batch_size = self.batch_size, shuffle=True)
        y_true = np.array([])
        y_pred = np.array([])
        with torch.no_grad():
            for i, (X, y) in enumerate(data_loader):
                y_true = np.hstack((y_true, y.numpy()))
                tmp = model(X.long().to(device))
                y_pred = np.hstack((y_pred, tmp.argmax(dim = -1).cpu().numpy()))
        
        tmp_f1 = f1_score(y_true.astype(int), y_pred.astype(int), average='weighted')
        if 'f1' not in self.result.keys() or tmp_f1 > self.result['f1']:
            self.result['f1'] = round(tmp_f1, 4)
            self.result['accuracy'] = round(accuracy_score(y_true.astype(int), y_pred.astype(int)), 4)
            self.result['precision'] = round(precision_score(y_true.astype(int), y_pred.astype(int), average='weighted'), 4)
            self.result['recall'] = round(recall_score(y_true.astype(int), y_pred.astype(int), average='weighted'), 4)
        
    def run(self, model, dataset_train, dataset_test, device):
        model = model.to(device)
        train_dataLoader = DataLoader(dataset_train, batch_size = self.batch_size, shuffle=True)
        optimizer = Adam(params = model.parameters(), lr = self.lr)
        Loss = nn.CrossEntropyLoss()
        for epoch in range(self.epochs):
            if epoch == 80:
                for param_group in optimizer.param_groups:
                    param_group['lr'] = self.lr / 10
            elif epoch == 140:
                for param_group in optimizer.param_groups:
                    param_group['lr'] = self.lr / 50        
            train_l_sum, train_acc_sum, n, batch_count, start = 0.0, 0.0, 0, 0, time.time()
            for i, (X, y_true) in enumerate(train_dataLoader):
                X = X.long().to(device)
                y_pred = model(X)
                l = Loss(y_pred, y_true.to(device))

                optimizer.zero_grad()
                l.backward()
                optimizer.step()
                train_l_sum += l.cpu().item()
                train_acc_sum += (y_pred.argmax(dim=1) == y_true.to(device)).sum().cpu().item()
                n += self.batch_size
                batch_count += 1

            model.eval() # 评估模式, 这会关闭dropout
            test_acc = self.evaluate_accuracy(model, dataset_test, device)
            print('epoch %d, loss %.4f, train acc %.4f, test acc %.4f, time %.1f sec'
                % (epoch + 1, train_l_sum / batch_count, train_acc_sum / n, test_acc, time.time() - start))
            self.train_log.append('epoch %d, loss %.4f, train acc %.4f, test acc %.4f, time %.1f sec'
                % (epoch + 1, train_l_sum / batch_count, train_acc_sum / n, test_acc, time.time() - start))
            
            if (epoch + 1) % 10 == 0:
                self.final_evaluate(model, dataset_test, device)
            model.train() # 改回训练模式
    
    def train(self):
        try:
            device = None
            if torch.cuda.is_available():
                device = torch.device('cuda',0)
                print('使用GPU')
            else:
                print('使用CPU')
            if not os.path.exists('logs'):
                os.mkdir('logs')
            dataset_train, dataset_test = self.load_dataset(0.2)
            model = RNN(self.max_payload_length, self.num_classes)
            print('开始训练...')
            start = time.time() 
            self.run(model, dataset_train, dataset_test, device)
            self.result['time'] = round(time.time() - start, 4)
            torch.save(model.state_dict(), os.path.join(self.model_dir, 'lstm_model.pkl'))
            print('训练结束...')
            self.result['status'] = "success"
            # 从train_log中截取信息
            epochList = []
            lossList = []
            trainAccList = []
            testAccList = []
            for data in self.train_log:
                epochList.append(data.split(',')[0].split(' ')[1])
                lossList.append(float(data.split(',')[1].split(' ')[2]))
                trainAccList.append(float(data.split(',')[2].split(' ')[3]))
                testAccList.append(float(data.split(',')[3].split(' ')[3]))
            
            self.result['epochList'] = epochList
            self.result['lossList'] = lossList
            self.result['trainAccList'] = trainAccList
            self.result['testAccList'] = testAccList
            return self.result
        except Exception as e:
            return {'status': 'fail', 'error':str(e)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='统计特征分类模型分类所需参数')
    parser.add_argument('dataset_dir')
    parser.add_argument('model_dir')

    args = parser.parse_args()
    # 待预测的csv文件目录,包含统计特征
    dataset_dir = args.dataset_dir # r'./dataset/Features/tcp'
    # 模型文件目录
    model_dir = args.model_dir # r'./weights

    class_dict = getClassInfo(os.path.join(model_dir, "lstm_ClassesInfo.txt"))
    lstm_train =LSTM_Train(dataset_dir, model_dir, class_dict)
    result = lstm_train.train()
    print(result)
