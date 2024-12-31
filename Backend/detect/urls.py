from django.urls import path, include
from rest_framework.routers import DefaultRouter
from detect import views

# router = DefaultRouter()
# router.register('index', views.index)

urlpatterns = [
    path('', views.index, name='index'),
    # 获取某ip的流量画像
    path('getIPImage', views.get_ip_image, name='get_ip_image'),
    # 生成IP流量画像
    path('genIPImage', views.gen_IP_image, name='gen_IP_image'),
    # 展示IP流量画像
    path('showIPImage', views.show_IP_image,  name='show_IP_image'),
    # 异常检测
    path('anomalyDetect', views.anomaly_detect, name='anomaly_detect'),
    # 异常记录查询
    path('showAnomaly', views.show_anomaly, name='show_anomaly'), 
    # 异常记录详情
    path('showAnomalyDetail', views.show_anomaly_detail, name='show_anomaly_detail')
]