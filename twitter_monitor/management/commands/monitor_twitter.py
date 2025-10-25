"""
监控 Twitter 用户的管理命令

使用方法:
    python manage.py monitor_twitter [username]
    
示例:
    python manage.py monitor_twitter                # 监控所有用户
    python manage.py monitor_twitter elonmusk       # 监控指定用户
"""

from django.core.management.base import BaseCommand, CommandError
from twitter_monitor.services import TwitterMonitorService
from twitter_monitor.models import MonitoredUser


class Command(BaseCommand):
    help = '监控 Twitter 用户的推文和回复'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            nargs='?',
            type=str,
            help='Twitter 用户名 (不带 @)，留空则监控所有用户'
        )

    def handle(self, *args, **options):
        service = TwitterMonitorService()
        username = options.get('username')
        
        if username:
            # 监控单个用户
            username = username.strip().lstrip('@')
            
            try:
                user = MonitoredUser.objects.get(username=username)
            except MonitoredUser.DoesNotExist:
                raise CommandError(f'用户 @{username} 不在监控列表中')
            
            self.stdout.write(f'开始监控用户 @{username}...')
            result = service.monitor_user(user)
            
            if result.get('status') == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ 监控完成: {result['tweets']} 条推文, "
                        f"{result['replies']} 条回复"
                    )
                )
            else:
                raise CommandError(f"监控失败: {result.get('error', '未知错误')}")
        else:
            # 监控所有用户
            self.stdout.write('开始监控所有用户...')
            result = service.monitor_all_users()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ 批量监控完成\n"
                    f"  总用户数: {result['total_users']}\n"
                    f"  成功: {result['success']}\n"
                    f"  失败: {result['failed']}\n"
                    f"  总推文: {result['total_tweets']}\n"
                    f"  总回复: {result['total_replies']}"
                )
            )
