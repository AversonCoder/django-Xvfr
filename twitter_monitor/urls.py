"""
Twitter Monitor URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'monitored-users', views.MonitoredUserViewSet, basename='monitoreduser')
router.register(r'tweets', views.TweetViewSet, basename='tweet')
router.register(r'replies', views.ReplyViewSet, basename='reply')
router.register(r'logs', views.MonitorLogViewSet, basename='monitorlog')

urlpatterns = [
    path('api/', include(router.urls)),
]
