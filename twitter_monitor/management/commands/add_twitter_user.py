"""
添加 Twitter 监控用户的管理命令

使用方法:
    python manage.py add_twitter_user <username>
    
示例:
    python manage.py add_twitter_user elonmusk
    python manage.py add_twitter_user openai
"""

from django.core.management.base import BaseCommand, CommandError
from twitter_monitor.services import TwitterMonitorService


class Command(BaseCommand):
    help = '添加 Twitter 监控用户'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Twitter 用户名 (不带 @)'
        )

    def handle(self, *args, **options):
        username = options['username'].strip().lstrip('@')
        
        self.stdout.write(f'正在添加用户 @{username}...')
        
        service = TwitterMonitorService()
        user = service.add_monitored_user(username)
        
        if user:
            self.stdout.write(
                self.style.SUCCESS(f'✓ 成功添加用户 @{username}')
            )
            self.stdout.write(f'  用户ID: {user.user_id}')
            self.stdout.write(f'  显示名: {user.display_name}')
        else:
            raise CommandError(f'无法找到用户 @{username}')
