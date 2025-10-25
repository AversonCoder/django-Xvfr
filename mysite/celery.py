"""
Celery 配置
"""

import os
from celery import Celery
from celery.schedules import crontab

# 设置 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

# 从 Django settings 中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()


# 配置定时任务
app.conf.beat_schedule = {
    'monitor-all-users-every-30-minutes': {
        'task': 'twitter_monitor.tasks.monitor_all_users_task',
        'schedule': crontab(minute='*/30'),  # 每30分钟执行一次
    },
    'cleanup-old-data-daily': {
        'task': 'twitter_monitor.tasks.cleanup_old_data_task',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨3点执行
        'kwargs': {'days': 30},  # 保留30天数据
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
