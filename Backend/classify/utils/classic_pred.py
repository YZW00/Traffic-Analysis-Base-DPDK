'''
功能:基于已有统计特征的分类模型权重,对目标流量(csv文件)预测,输出预测结果
参数:
    dataset_dir: 待预测的csv文件目录,包含统计特征
    model_dir: 模型文件目录, 类别字典classic_ClassesInfo.txt
    threshold: 阈值,大于阈值则为正常流量,小于阈值则为未知流量
输出:与待预测csv文件同名的txt文件,包含文字标签预测结果

运行示例: python3 classic_pred.py ../dataset/Features/tcp ../weights 0.5
'''
import joblib
import os, time
import pandas as pd
import numpy as np
import argparse
import ipaddress
from sklearn.preprocessing import StandardScaler # 归一化
from .getClassInfo import getClassInfo

class Classic_Pred:
    def __init__(self, dataset_dir, model_dir, threshold, class_dict):
        self.dataset_dir = dataset_dir
        self.model_dir = model_dir
        self.threshold = threshold
        self.class_dict = class_dict

    def pred(self):
        try:
            x_test = pd.read_csv(os.path.join(self.dataset_dir, 'statistical.csv'), index_col=False, header=None)
            # 将IP地址转换为整数
            x_test[0] = x_test[0].apply(lambda x: int(ipaddress.ip_address(x)))
            x_test[1] = x_test[1].apply(lambda x: int(ipaddress.ip_address(x)))

            # 归一化操作
            scaler = StandardScaler()
            x_test = scaler.fit_transform(x_test.values)
            
            start = time.time()
            # 模型加载
            best_model = joblib.load(os.path.join(self.model_dir, 'classic_model.m'))
        
            # 预测
            # y_pred = best_model.predict(x_test)
            y_pred_prob = best_model.predict_proba(x_test)
            my_pred = np.array([np.argmax(pred) for pred in y_pred_prob])
            prob_pred = np.array([np.max(pred) for pred in y_pred_prob])
            
            # 若预测概率小于阈值,则预测为-1(未知类别)
            my_pred[prob_pred < self.threshold] = -1
            # print(my_pred)
            
            # 预测结果转化为类别名称
            pred_class = []
            for p in my_pred:
                if p == -1:
                    pred_class.append('未知')
                else:
                    pred_class.append(self.class_dict[p])
            
            duration = time.time() - start
            # 保存到txt
            # fileName = dataset_dir.split('/')[-1].split('.')[0]
            # with open(fileName + '_pred.txt', 'w', encoding='utf-8') as f:
            #     for p in pred_class:
            #         f.write(p + '\n')
            # print('预测完成！')
            return {'pred':list(pred_class), 'prob':list(prob_pred), 'time':duration, 'status':"success"}
        except Exception as e:
            return {'status': 'fail', 'error':str(e)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='统计特征分类模型分类所需参数')
    parser.add_argument('dataset_dir')
    parser.add_argument('model_dir')
    parser.add_argument('threshold', type=float)
    args = parser.parse_args()

    # 待预测的csv文件目录,包含统计特征
    dataset_dir = args.dataset_dir
    # 模型文件目录
    model_dir = args.model_dir # r'./classic_model.m'
    # 置信度阈值
    threshold = args.threshold # 0.5

    class_dict = getClassInfo(os.path.join(model_dir, "classic_ClassesInfo.txt"))

    classic_model = Classic_pred(dataset_dir, model_dir, threshold, class_dict)
    pred_class = classic_model.pred()
    print(pred_class)