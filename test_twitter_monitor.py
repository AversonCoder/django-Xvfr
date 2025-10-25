#!/usr/bin/env python
"""
Twitter 监控系统测试脚本

在配置好 Twitter API 后运行此脚本测试功能
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from twitter_monitor.models import MonitoredUser, Tweet, Reply
from twitter_monitor.services import TwitterMonitorService


def test_twitter_api():
    """测试 Twitter API 连接"""
    print("=" * 60)
    print("测试 1: Twitter API 连接")
    print("=" * 60)
    
    try:
        from twitter_monitor.services import TwitterService
        service = TwitterService()
        print("✓ Twitter API 初始化成功")
        return True
    except ValueError as e:
        print(f"✗ Twitter API 配置错误: {e}")
        print("\n请设置环境变量 TWITTER_BEARER_TOKEN")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_add_user():
    """测试添加监控用户"""
    print("\n" + "=" * 60)
    print("测试 2: 添加监控用户")
    print("=" * 60)
    
    # 使用 Twitter 官方账号作为测试
    test_username = "Twitter"
    
    try:
        service = TwitterMonitorService()
        user = service.add_monitored_user(test_username)
        
        if user:
            print(f"✓ 成功添加用户 @{test_username}")
            print(f"  用户ID: {user.user_id}")
            print(f"  显示名: {user.display_name}")
            print(f"  头像: {user.profile_image_url}")
            return user
        else:
            print(f"✗ 无法添加用户 @{test_username}")
            return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def test_monitor_user(user):
    """测试监控用户"""
    print("\n" + "=" * 60)
    print("测试 3: 监控用户推文")
    print("=" * 60)
    
    if not user:
        print("✗ 跳过测试 (无有效用户)")
        return
    
    try:
        service = TwitterMonitorService()
        result = service.monitor_user(user)
        
        if result.get('status') == 'success':
            print(f"✓ 监控成功")
            print(f"  新推文: {result['tweets']} 条")
            print(f"  新回复: {result['replies']} 条")
        else:
            print(f"✗ 监控失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"✗ 错误: {e}")


def test_query_data():
    """测试查询数据"""
    print("\n" + "=" * 60)
    print("测试 4: 查询数据库")
    print("=" * 60)
    
    # 查询监控用户
    users_count = MonitoredUser.objects.count()
    print(f"监控用户总数: {users_count}")
    
    # 查询推文
    tweets_count = Tweet.objects.count()
    print(f"推文总数: {tweets_count}")
    
    if tweets_count > 0:
        latest_tweet = Tweet.objects.order_by('-created_at').first()
        print(f"\n最新推文:")
        print(f"  作者: @{latest_tweet.author.username}")
        print(f"  内容: {latest_tweet.text[:100]}")
        print(f"  时间: {latest_tweet.created_at}")
        print(f"  点赞: {latest_tweet.like_count}")
        print(f"  转发: {latest_tweet.retweet_count}")
    
    # 查询回复
    replies_count = Reply.objects.count()
    print(f"\n回复总数: {replies_count}")


def main():
    """主测试流程"""
    print("\n🚀 Twitter 监控系统测试\n")
    
    # 测试 1: API 连接
    if not test_twitter_api():
        print("\n❌ 测试失败: 请先配置 Twitter API")
        return
    
    # 测试 2: 添加用户
    user = test_add_user()
    
    # 测试 3: 监控用户
    test_monitor_user(user)
    
    # 测试 4: 查询数据
    test_query_data()
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)
    print("\n提示:")
    print("1. 访问 http://localhost:8000/admin/ 查看管理后台")
    print("2. 访问 http://localhost:8000/twitter/api/monitored-users/ 查看 API")
    print("3. 运行 'python manage.py monitor_twitter' 手动监控")
    print("4. 启动 Celery 实现自动监控")


if __name__ == '__main__':
    main()
