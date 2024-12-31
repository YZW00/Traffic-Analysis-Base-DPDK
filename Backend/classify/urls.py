from django.urls import path, include
from rest_framework.routers import DefaultRouter
from classify import views

# router = DefaultRouter()
# router.register('index', views.index)

urlpatterns = [
    path('', views.index, name='index'),
    # 数据集目录遍历
    path('showDir', views.show_dir, name='show_dir'),
    # 业务分类模型预测
    path('modelPredCsv', views.model_pred_csv, name='model_pred_csv'),
    # 业务分类模型训练
    path('modelTrainCsv', views.model_train_csv, name='model_train_csv'),
    # A3C采集
    path('A3CRun', views.A3C_run, name='A3C_run'),
    # 业务类别信息获取与修改
    path('splitConfig', views.split_config, name='split_config'),
    # pcap划分
    path('pcapSplit', views.pcap_split, name='pcap_split'),
    # 数据集构建(特征提取)
    path('datasetBuild', views.pcap_feature_extract, name='pcap_feature_extract'),
    # 上传pcap文件
    path('uploadFiles', views.upload_files, name='upload_files'),
    # 数据库 业务分类预测
    path('modelPredSQL', views.model_pred_mysql, name="views"),
    # 查看数据库特征表
    path('getFlowTab', views.get_flow_table, name='get_flow_table'),
]