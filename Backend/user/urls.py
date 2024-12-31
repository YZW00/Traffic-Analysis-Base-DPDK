from user import views
from django.urls import path
# router = DefaultRouter()
# router.register('index', views.index)

urlpatterns = [
    path('', views.login, name='login')
]