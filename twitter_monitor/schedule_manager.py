"""
监控定时任务管理器
用于动态更新 Celery Beat 定时任务配置
"""

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


def update_monitoring_schedule(interval_type, **kwargs):
    """
    更新监控任务的定时配置
    
    Args:
        interval_type: 'interval' 或 'crontab'
        kwargs: 定时配置参数
            - 对于 interval: interval_minutes (int)
            - 对于 crontab: minute, hour, day_of_week (str)
    
    Returns:
        bool: 是否成功更新
    """
    task_name = 'twitter_monitor.tasks.monitor_all_users_task'
    periodic_task_name = 'monitor-all-users-periodic'
    
    try:
        if interval_type == 'interval':
            # 使用时间间隔（例如：每 30 分钟）
            interval_minutes = kwargs.get('interval_minutes', 30)
            
            # 获取或创建 IntervalSchedule
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=interval_minutes,
                period=IntervalSchedule.MINUTES,
            )
            
            # 更新或创建 PeriodicTask
            periodic_task, _ = PeriodicTask.objects.update_or_create(
                name=periodic_task_name,
                defaults={
                    'interval': schedule,
                    'task': task_name,
                    'enabled': True,
                    'crontab': None,  # 清除 crontab 配置
                }
            )
            
            return True
            
        elif interval_type == 'crontab':
            # 使用 Crontab（例如：自定义时间）
            minute = kwargs.get('minute', '*/30')
            hour = kwargs.get('hour', '*')
            day_of_week = kwargs.get('day_of_week', '*')
            
            # 获取或创建 CrontabSchedule
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month='*',
                month_of_year='*',
            )
            
            # 更新或创建 PeriodicTask
            periodic_task, _ = PeriodicTask.objects.update_or_create(
                name=periodic_task_name,
                defaults={
                    'crontab': schedule,
                    'task': task_name,
                    'enabled': True,
                    'interval': None,  # 清除 interval 配置
                }
            )
            
            return True
            
    except Exception as e:
        print(f"更新定时任务失败: {str(e)}")
        return False


def stop_monitoring_schedule():
    """
    停止监控定时任务
    
    Returns:
        bool: 是否成功停止
    """
    periodic_task_name = 'monitor-all-users-periodic'
    
    try:
        # 禁用定时任务
        PeriodicTask.objects.filter(name=periodic_task_name).update(enabled=False)
        return True
    except Exception as e:
        print(f"停止定时任务失败: {str(e)}")
        return False


def get_current_schedule():
    """
    获取当前的定时任务配置
    
    Returns:
        dict: 当前配置信息
    """
    periodic_task_name = 'monitor-all-users-periodic'
    
    try:
        task = PeriodicTask.objects.filter(name=periodic_task_name).first()
        
        if not task:
            return {
                'enabled': False,
                'type': None,
                'schedule': None,
            }
        
        if task.interval:
            return {
                'enabled': task.enabled,
                'type': 'interval',
                'schedule': f'每 {task.interval.every} {task.interval.period}',
                'interval_minutes': task.interval.every if task.interval.period == 'minutes' else None,
            }
        elif task.crontab:
            return {
                'enabled': task.enabled,
                'type': 'crontab',
                'schedule': f'Cron: {task.crontab.minute} {task.crontab.hour} * * {task.crontab.day_of_week}',
                'crontab': {
                    'minute': task.crontab.minute,
                    'hour': task.crontab.hour,
                    'day_of_week': task.crontab.day_of_week,
                }
            }
        
        return {
            'enabled': False,
            'type': None,
            'schedule': None,
        }
        
    except Exception as e:
        print(f"获取定时任务配置失败: {str(e)}")
        return {
            'enabled': False,
            'type': None,
            'schedule': None,
        }
