"""
Twitter Monitor URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import web_views

app_name = 'twitter_monitor'

router = DefaultRouter()
router.register(r'monitored-users', views.MonitoredUserViewSet, basename='monitoreduser')
router.register(r'tweets', views.TweetViewSet, basename='tweet')
router.register(r'replies', views.ReplyViewSet, basename='reply')
router.register(r'logs', views.MonitorLogViewSet, basename='monitorlog')

urlpatterns = [
    # Web 可视化界面
    path('', web_views.dashboard, name='dashboard'),
    path('add-user/', web_views.add_user, name='add_user'),
    path('monitor-config/', web_views.monitor_config, name='monitor_config'),
    path('start-monitoring/', web_views.start_monitoring, name='start_monitoring'),
    path('user/<int:user_id>/', web_views.user_detail, name='user_detail'),
    path('api-docs/', web_views.api_docs, name='api_docs'),
    path('logs/', web_views.logs, name='logs'),  # 新增：日志页面
    path('test-api/', web_views.test_api, name='test_api'),  # 新增：API 测试
    
    # REST API
    path('api/', include(router.urls)),
]
