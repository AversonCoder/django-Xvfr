"""
Celery 定时任务
"""

from celery import shared_task
from django.utils import timezone
import logging

from .services import TwitterMonitorService
from .models import MonitoredUser

logger = logging.getLogger(__name__)


@shared_task
def monitor_all_users_task():
    """
    监控所有启用的用户 (定时任务)
    """
    logger.info("开始执行定时监控任务")
    
    service = TwitterMonitorService()
    result = service.monitor_all_users()
    
    logger.info(f"定时监控任务完成: {result}")
    return result


@shared_task
def monitor_single_user_task(user_id):
    """
    监控单个用户 (异步任务)
    
    Args:
        user_id: MonitoredUser 的 ID
    """
    try:
        user = MonitoredUser.objects.get(id=user_id)
        service = TwitterMonitorService()
        result = service.monitor_user(user)
        logger.info(f"监控用户 @{user.username} 完成: {result}")
        return result
    except MonitoredUser.DoesNotExist:
        logger.error(f"用户不存在: ID={user_id}")
        return {'error': 'User not found'}
    except Exception as e:
        logger.error(f"监控用户失败: {str(e)}")
        return {'error': str(e)}


@shared_task
def cleanup_old_data_task(days=30):
    """
    清理旧数据 (定时任务)
    
    Args:
        days: 保留最近多少天的数据
    """
    from datetime import timedelta
    from .models import Tweet, Reply, MonitorLog
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # 删除旧推文
    old_tweets = Tweet.objects.filter(created_at__lt=cutoff_date)
    tweets_count = old_tweets.count()
    old_tweets.delete()
    
    # 删除旧回复
    old_replies = Reply.objects.filter(created_at__lt=cutoff_date)
    replies_count = old_replies.count()
    old_replies.delete()
    
    # 删除旧日志
    old_logs = MonitorLog.objects.filter(created_at__lt=cutoff_date)
    logs_count = old_logs.count()
    old_logs.delete()
    
    logger.info(f"清理完成: 删除 {tweets_count} 条推文, {replies_count} 条回复, {logs_count} 条日志")
    
    return {
        'tweets_deleted': tweets_count,
        'replies_deleted': replies_count,
        'logs_deleted': logs_count,
    }
