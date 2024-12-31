from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('start_capture/', views.start_capture),
    path('view_pcaps/', views.view_pcaps),
    path('stop_capture/', views.stop_capture),
    path('start_feature_extract/', views.start_feature_extract),
    path('stop_feature_extract/', views.stop_feature_extract),
    # path('',views.init)
]
