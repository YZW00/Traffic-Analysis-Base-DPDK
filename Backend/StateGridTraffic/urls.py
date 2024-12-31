"""StateGridTraffic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from packet_dissect import views
from packet_dissect import sharkd_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('traffic_collect/', include('traffic_collect.urls')),
    path('classify/', include('classify.urls')),
    path('detect/', include('detect.urls')),
    path('login/', include('user.urls')),
    path('statistic_result/',views.packet_outline),
    path('statistic_initial/', views.packet_main),
    path('page_request/', views.fragment_data),
    path('stream/', views.stream),
    path("creat_session", sharkd_views.creat_session),
    path("close_session", sharkd_views.close_session),
    path("session_request", sharkd_views.session_request),
    path("redis_test", sharkd_views.redis_test)
]
