"""
Web 可视化界面视图
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from celery.schedules import crontab

from .models import MonitoredUser, Tweet, Reply, MonitorLog
from .services import TwitterMonitorService
from .tasks import monitor_all_users_task
from .schedule_manager import update_monitoring_schedule, stop_monitoring_schedule, get_current_schedule


def dashboard(request):
    """
    主控制台
    """
    # 统计数据
    total_users = MonitoredUser.objects.count()
    active_users = MonitoredUser.objects.filter(is_active=True).count()
    
    # 最近30天的数据
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_tweets = Tweet.objects.filter(created_at__gte=thirty_days_ago).count()
    total_replies = Reply.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # 监控日志
    monitor_logs_count = MonitorLog.objects.count()
    last_log = MonitorLog.objects.order_by('-created_at').first()
    last_monitor_time = last_log.created_at.strftime('%m-%d %H:%M') if last_log else '暂无记录'
    
    # 用户列表
    users = MonitoredUser.objects.all().order_by('-created_at')[:10]
    
    # 检查 API 可用性
    api_available = True
    try:
        from .services import TwitterService
        service = TwitterService()
        # 简单检查，不实际调用 API
        api_available = bool(service.client)
    except:
        api_available = False
    
    context = {
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'total_tweets': total_tweets,
            'total_replies': total_replies,
            'monitor_logs': monitor_logs_count,
            'last_monitor_time': last_monitor_time,
        },
        'users': users,
        'api_available': api_available,
    }
    
    return render(request, 'twitter_monitor/dashboard.html', context)


def add_user(request):
    """
    添加监控用户
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lstrip('@')
        
        if not username:
            messages.error(request, '请输入 Twitter 用户名')
            return redirect('twitter_monitor:add_user')
        
        # 检查是否已存在
        if MonitoredUser.objects.filter(username=username).exists():
            messages.warning(request, f'用户 @{username} 已在监控列表中')
            return redirect('twitter_monitor:dashboard')
        
        # 添加用户
        try:
            service = TwitterMonitorService()
            user = service.add_monitored_user(username)
            
            if user:
                messages.success(request, f'成功添加监控用户 @{username}')
                return redirect('twitter_monitor:dashboard')
            else:
                messages.error(request, f'无法找到用户 @{username}，请检查用户名是否正确')
        except Exception as e:
            messages.error(request, f'添加失败: {str(e)}')
    
    return render(request, 'twitter_monitor/add_user.html')


def monitor_config(request):
    """
    监控配置页面
    """
    users = MonitoredUser.objects.all().order_by('username')
    active_users_count = MonitoredUser.objects.filter(is_active=True).count()
    
    # 获取当前监控状态（从 Celery Beat 或数据库）
    monitoring_active = active_users_count > 0
    current_interval = "每 30 分钟"  # 默认值，可以从配置中读取
    next_run_time = None
    
    context = {
        'users': users,
        'active_users_count': active_users_count,
        'monitoring_active': monitoring_active,
        'current_interval': current_interval,
        'next_run_time': next_run_time,
    }
    
    return render(request, 'twitter_monitor/monitor_config.html', context)


def start_monitoring(request):
    """
    启动/停止监控
    """
    if request.method != 'POST':
        return redirect('twitter_monitor:monitor_config')
    
    action = request.POST.get('action')
    
    if action == 'start':
        # 获取选中的用户
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.warning(request, '请至少选择一个用户')
            return redirect('twitter_monitor:monitor_config')
        
        # 更新用户状态
        MonitoredUser.objects.all().update(is_active=False)
        MonitoredUser.objects.filter(id__in=user_ids).update(is_active=True)
        
        # 获取监控频率
        interval = request.POST.get('interval')
        
        # 处理频率配置
        frequency_text = ''
        schedule_updated = False
        
        if interval == 'custom':
            # 自定义频率
            custom_minute = request.POST.get('custom_minute', '*/30')
            custom_hour = request.POST.get('custom_hour', '*')
            custom_day_of_week = request.POST.get('custom_day_of_week', '*')
            
            frequency_text = f'自定义（分钟:{custom_minute}, 小时:{custom_hour}, 星期:{custom_day_of_week}）'
            
            # 更新 Celery Beat 定时任务
            schedule_updated = update_monitoring_schedule(
                'crontab',
                minute=custom_minute,
                hour=custom_hour,
                day_of_week=custom_day_of_week
            )
        else:
            # 预设频率
            interval_minutes = int(interval)
            frequency_text = f'每 {interval_minutes} 分钟'
            
            # 更新 Celery Beat 定时任务
            schedule_updated = update_monitoring_schedule(
                'interval',
                interval_minutes=interval_minutes
            )
        
        # 立即执行一次监控
        try:
            # 尝试使用 Celery 异步执行
            try:
                monitor_all_users_task.delay()
                task_msg = '已加入任务队列'
            except Exception as celery_error:
                # 如果 Celery/Redis 不可用，记录警告但不中断流程
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Celery 不可用，请检查 Redis 服务: {str(celery_error)}')
                task_msg = '⚠️ 定时任务服务未启动，请在 Railway 添加 Redis 服务'
            
            messages.success(
                request, 
                f'监控已启动！已选择 {len(user_ids)} 个用户，监控频率: {frequency_text}。{task_msg}'
            )
        except Exception as e:
            messages.error(request, f'启动失败: {str(e)}')
    
    elif action == 'stop':
        # 停止所有监控
        MonitoredUser.objects.all().update(is_active=False)
        
        # 禁用定时任务
        stop_monitoring_schedule()
        
        messages.info(request, '监控已停止')
    
    return redirect('twitter_monitor:monitor_config')


def user_detail(request, user_id):
    """
    用户详情页面
    """
    user = get_object_or_404(MonitoredUser, id=user_id)
    
    # 用户的推文
    tweets = user.tweets.all().order_by('-created_at')[:20]
    
    # 用户的回复
    replies = user.replies.all().order_by('-created_at')[:20]
    
    # 监控日志
    logs = user.logs.all().order_by('-created_at')[:10]
    
    # 统计
    total_tweets = user.tweets.count()
    total_replies = user.replies.count()
    
    context = {
        'user': user,
        'tweets': tweets,
        'replies': replies,
        'logs': logs,
        'total_tweets': total_tweets,
        'total_replies': total_replies,
    }
    
    return render(request, 'twitter_monitor/user_detail.html', context)


def api_docs(request):
    """
    API 文档页面
    """
    return render(request, 'twitter_monitor/api_docs.html')


def logs(request):
    """
    监控日志页面
    """
    # 获取最近 100 条日志
    logs = MonitorLog.objects.all().order_by('-created_at')[:100]
    
    # 统计数据
    total_logs = MonitorLog.objects.count()
    success_logs = MonitorLog.objects.filter(status='success').count()
    failed_logs = MonitorLog.objects.filter(status='failed').count()
    total_tweets = sum(MonitorLog.objects.values_list('tweets_fetched', flat=True))
    total_replies = sum(MonitorLog.objects.values_list('replies_fetched', flat=True))
    
    context = {
        'logs': logs,
        'stats': {
            'total': total_logs,
            'success': success_logs,
            'failed': failed_logs,
            'total_tweets': total_tweets,
            'total_replies': total_replies,
        }
    }
    
    return render(request, 'twitter_monitor/logs.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def test_api(request):
    """
    测试 Twitter API 连接
    """
    try:
        from .services import TwitterService
        from django.conf import settings
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("开始测试 Twitter API")
        
        # 检查环境变量
        bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', '')
        
        if not bearer_token:
            return JsonResponse({
                'success': False,
                'error': 'TWITTER_BEARER_TOKEN 环境变量未配置！',
                'hint': '请在 Railway Variables 中添加 TWITTER_BEARER_TOKEN'
            })
        
        # 显示 Token 前几位（隐藏敏感信息）
        token_preview = bearer_token[:20] + '...' if len(bearer_token) > 20 else bearer_token
        logger.info(f"Bearer Token: {token_preview}")
        
        # 创建服务，不等待速率限制
        service = TwitterService(wait_on_rate_limit=False)
        
        # 测试：获取 Twitter 官方账号信息
        user_info = service.get_user_by_username('Twitter')
        
        if user_info:
            logger.info(f"API 测试成功：{user_info}")
            return JsonResponse({
                'success': True,
                'message': 'API 连接成功！',
                'result': {
                    'user_id': user_info['user_id'],
                    'username': user_info['username'],
                    'display_name': user_info['display_name'],
                    'api_working': True,
                    'test_account': '@Twitter',
                    'token_configured': True,
                    'token_preview': token_preview
                }
            })
        else:
            logger.error("API 调用失败：无法获取用户信息")
            return JsonResponse({
                'success': False,
                'error': 'API 调用失败：无法获取用户信息',
                'possible_reasons': [
                    '1. API 密钥配置错误或已过期',
                    '2. 免费版 API 无法使用该端点（需要 Basic 级别）',
                    '3. Bearer Token 格式错误',
                    '4. Twitter API 服务不可用'
                ],
                'token_configured': True,
                'token_preview': token_preview,
                'next_steps': '请访问 https://developer.twitter.com/en/portal/dashboard 检查 API 密钥和订阅级别'
            })
    except ValueError as e:
        # 捕获我们自己抛出的异常（速率限制、权限不足等）
        error_msg = str(e)
        logger.error(f"API 测试失败: {error_msg}")
        
        if "API 速率限制" in error_msg:
            return JsonResponse({
                'success': False,
                'error': '⚠️ Twitter API 速率限制',
                'message': '您的 API 调用次数已达到上限，请稍后再试。',
                'hint': '免费版 API 每 15 分钟只有 15 次调用机会，请升级到 Basic 级别获得更多配额。',
                'wait_time': '请等待 10-15 分钟后重试'
            })
        elif "免费版" in error_msg or "权限不足" in error_msg:
            return JsonResponse({
                'success': False,
                'error': '❌ API 权限不足',
                'message': '免费版 Twitter API 无法使用监控功能。',
                'reason': '当前代码调用的端点需要 Basic 级别（$100/月）或以上。',
                'solution': '请访问 https://developer.twitter.com/en/portal/products 升级你的订阅。',
                'alternatives': [
                    '升级到 Basic 级别 ($100/月)',
                    '等待 Twitter 降低 API 门槛',
                    '使用其他社交媒体平台的 API'
                ]
            })
        elif "密钥错误" in error_msg or "已过期" in error_msg:
            return JsonResponse({
                'success': False,
                'error': '❌ API 密钥错误',
                'message': 'Twitter API 密钥配置错误或已过期。',
                'next_steps': [
                    '1. 访问 https://developer.twitter.com/en/portal/dashboard',
                    '2. 检查密钥是否还有效',
                    '3. 如果已撤销，重新生成并更新 Railway 环境变量'
                ]
            })
        else:
            return JsonResponse({
                'success': False,
                'error': error_msg
            })
    except Exception as e:
        logger.error(f"API 测试异常：{str(e)}")
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'异常：{str(e)}',
            'traceback': traceback.format_exc(),
            'hint': '请检查 Railway 日志获取详细错误信息'
        })
