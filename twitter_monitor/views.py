"""
REST API 视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import MonitoredUser, Tweet, Reply, MonitorLog
from .serializers import (
    MonitoredUserSerializer, TweetSerializer,
    ReplySerializer, MonitorLogSerializer
)
from .services import TwitterMonitorService
from .tasks import monitor_single_user_task


class MonitoredUserViewSet(viewsets.ModelViewSet):
    """监控用户 API"""
    queryset = MonitoredUser.objects.all()
    serializer_class = MonitoredUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['username', 'display_name']
    ordering_fields = ['created_at', 'last_checked_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def add_user(self, request):
        """
        添加监控用户
        POST /api/monitored-users/add_user/
        Body: {"username": "twitter_username"}
        """
        username = request.data.get('username', '').strip().lstrip('@')
        
        if not username:
            return Response(
                {'error': '请提供 Twitter 用户名'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已存在
        if MonitoredUser.objects.filter(username=username).exists():
            return Response(
                {'error': f'用户 @{username} 已在监控列表中'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 添加用户
        service = TwitterMonitorService()
        user = service.add_monitored_user(username)
        
        if not user:
            return Response(
                {'error': f'无法找到用户 @{username}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def monitor_now(self, request, pk=None):
        """
        立即监控指定用户
        POST /api/monitored-users/{id}/monitor_now/
        """
        user = self.get_object()
        
        # 异步执行监控任务
        task = monitor_single_user_task.delay(user.id)
        
        return Response({
            'message': f'已启动监控任务',
            'task_id': task.id,
            'username': user.username
        })
    
    @action(detail=False, methods=['post'])
    def monitor_all(self, request):
        """
        监控所有启用的用户
        POST /api/monitored-users/monitor_all/
        """
        from .tasks import monitor_all_users_task
        
        task = monitor_all_users_task.delay()
        
        return Response({
            'message': '已启动批量监控任务',
            'task_id': task.id
        })


class TweetViewSet(viewsets.ReadOnlyModelViewSet):
    """推文 API (只读)"""
    queryset = Tweet.objects.select_related('author').all()
    serializer_class = TweetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'tweet_type', 'has_media']
    search_fields = ['text', 'tweet_id']
    ordering_fields = ['created_at', 'like_count', 'retweet_count']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """
        获取推文的所有回复
        GET /api/tweets/{id}/replies/
        """
        tweet = self.get_object()
        replies = tweet.replies.select_related('author').all()
        serializer = ReplySerializer(replies, many=True)
        return Response(serializer.data)


class ReplyViewSet(viewsets.ReadOnlyModelViewSet):
    """回复 API (只读)"""
    queryset = Reply.objects.select_related('author', 'tweet').all()
    serializer_class = ReplySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'tweet']
    search_fields = ['text', 'reply_id']
    ordering_fields = ['created_at', 'like_count']
    ordering = ['-created_at']


class MonitorLogViewSet(viewsets.ReadOnlyModelViewSet):
    """监控日志 API (只读)"""
    queryset = MonitorLog.objects.select_related('user').all()
    serializer_class = MonitorLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
