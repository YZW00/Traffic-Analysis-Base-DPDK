'''
功能:基于统计特征分别训练给定的几种分类模型,将效果最优的模型保存为.m文件
参数:
    dataset_dir: 数据集文件目录,包含统计特征csv、标签csv
    model_dir: 模型权重的保存目录, ,命名为classic_model.m
输出:与待预测csv文件同名的txt文件,包含文字标签预测结果
运行示例: python3 classic_train.py ../dataset/Features/tcp ../weights
'''
import os, sys, time
import argparse
import numpy as np
import joblib
import shutil
import pandas as pd
import ipaddress
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler  # 归一化
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score
from sklearn.model_selection import RandomizedSearchCV

class Classic_Train:
    def __init__(self, dataset_dir, model_dir):
        self.dataset_dir = dataset_dir
        self.model_dir = model_dir
        self.best_model = None
        self.best_score = 0.0
        self.best_dtc = None
        self.Classifier = None
        self.result = {'RandomForest':{}, 'DecisionTree':{}, 'AdaBoost':{}}
        # 读取类别信息
        shutil.copyfile(os.path.join(dataset_dir, "ClassesInfo.txt"), os.path.join(model_dir, "classic_ClassesInfo.txt"))
    
    def Dataset_loader(self):
        # 数据集文件
        dataset = pd.read_csv(os.path.join(self.dataset_dir, 'statistical.csv'), index_col=False, header=None)
        # 将IP地址转换为整数
        dataset[0] = dataset[0].apply(lambda x: int(ipaddress.ip_address(x)))
        dataset[1] = dataset[1].apply(lambda x: int(ipaddress.ip_address(x)))
        labelset = np.loadtxt(os.path.join(self.dataset_dir, 'label.csv'), delimiter=',')
        # dataset数据部分作为数据集
        x_train, x_test, y_train, y_test = train_test_split(dataset.values, labelset, test_size=0.2, shuffle=True)
        # 归一化操作
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x_train)
        x_test = scaler.transform(x_test)
        return x_train, x_test, y_train.ravel(), y_test.ravel()

    def RandomForest(self):
        rfc = RandomForestClassifier()
        param_grid = {
            'n_estimators': np.arange(78, 120, 2),
            'max_depth': np.arange(13, 36, 2)
        }  # param_grid:我们要调参数的列表(带有参数名称作为键的字典)
        return rfc, param_grid

    def DecisionTree(self):
        rtc = DecisionTreeClassifier()
        param_grid = {
            'criterion': ['entropy','gini'],
            'max_depth': np.arange(10, 100, 2),
            'min_samples_split': np.arange(2, 12, 1)
        }  # param_grid:我们要调参数的列表(带有参数名称作为键的字典)
        return rtc, param_grid
    
    def AdaBoost(self):
        adb = AdaBoostClassifier(self.best_dtc)
        param_grid = {
            'n_estimators': np.arange(30, 100, 5),
            'learning_rate': np.arange(0.1, 3, 0.2)
        }
        return adb, param_grid

    def GridSearch(self, model, param_grid, x_train, x_test, y_train, y_test, MODEL):
        grid_search = RandomizedSearchCV(model, param_grid, n_jobs=4, verbose=0, scoring='f1_weighted', cv=3, n_iter=30, refit=True)
        grid_search.fit(x_train, y_train)  # 训练
        # 当前最佳模型
        model = grid_search.best_estimator_
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        self.result[MODEL]['accuracy'] = round(accuracy_score(y_test, y_pred), 4)
        self.result[MODEL]['recall'] = round(recall_score(y_test, y_pred, average='weighted'), 4)
        self.result[MODEL]['precision'] = round(precision_score(y_test, y_pred, average='weighted'), 4)
        self.result[MODEL]['f1'] = round(f1_score(y_test, y_pred, average='weighted'), 4)
        print("best f1:", f1_score(y_test, y_pred, average='weighted'))
        # 更新最高分模型
        if grid_search.best_score_ > self.best_score:
            self.best_score = grid_search.best_score_
            self.best_model = model

        if MODEL == 'DecisionTree':
            self.best_dtc = model
    
    def train(self):
        try:
            for MODEL in ['RandomForest', 'DecisionTree', 'AdaBoost']:
                start = time.time()
                if MODEL == 'RandomForest':
                    self.Classifier = self.RandomForest
                elif MODEL == 'AdaBoost':
                    self.Classifier = self.AdaBoost
                elif MODEL == 'DecisionTree':
                    self.Classifier = self.DecisionTree

                x_train, x_test, y_train, y_test = self.Dataset_loader()
                print(MODEL)
                model, param_grid = self.Classifier()
                self.GridSearch(model, param_grid, x_train, x_test, y_train, y_test, MODEL)
                self.result[MODEL]['time'] = round(time.time() - start, 4)
            joblib.dump(self.best_model, os.path.join(self.model_dir, 'classic_model.m'))
            self.result['status'] = "success"
            return self.result
            print('训练完成!')
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
    model_dir = args.model_dir # r'./classic_model.m'

    # 训练模型
    model = Classic_Train(dataset_dir, model_dir)
    model.train()
