#!/usr/bin/env python
"""
快速启动脚本 - 测试 Twitter API 并添加监控用户
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from twitter_monitor.services import TwitterService, TwitterMonitorService
from twitter_monitor.models import MonitoredUser


def main():
    print("\n" + "=" * 70)
    print("🚀 Twitter 监控系统 - 快速启动")
    print("=" * 70)
    
    # 步骤 1: 检查 API 配置
    print("\n📌 步骤 1: 检查 Twitter API 配置")
    print("-" * 70)
    
    try:
        service = TwitterService()
        print("✅ Twitter API 配置成功")
        print(f"   Bearer Token 已加载")
    except Exception as e:
        print(f"❌ Twitter API 配置失败: {e}")
        print("\n请检查 .env 文件中的 TWITTER_BEARER_TOKEN 是否正确")
        return
    
    # 步骤 2: 测试 API 连接（使用一个简单的请求）
    print("\n📌 步骤 2: 测试 API 连接")
    print("-" * 70)
    
    try:
        # 测试获取自己的用户信息（使用 Access Token）
        print("正在测试 API 连接...")
        
        # 由于我们只有 Bearer Token，我们尝试搜索一个公开的推文
        test_user = "Twitter"
        print(f"尝试获取用户信息: @{test_user}")
        
        user_info = service.get_user_by_username(test_user)
        if user_info:
            print(f"✅ API 连接成功！")
            print(f"   测试用户: @{user_info['username']}")
            print(f"   显示名称: {user_info['display_name']}")
        else:
            print("⚠️  API 连接正常，但无法获取用户信息")
            print("   这可能是因为:")
            print("   1. Twitter API 免费版限制")
            print("   2. 需要升级 API 访问级别")
            print("   3. Bearer Token 权限不足")
            
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        print("\n可能的原因:")
        print("1. Twitter API 密钥无效")
        print("2. API 访问级别不足（需要升级到 Basic 或更高）")
        print("3. 网络连接问题")
        return
    
    # 步骤 3: 查看当前监控用户
    print("\n📌 步骤 3: 当前监控用户")
    print("-" * 70)
    
    users = MonitoredUser.objects.all()
    if users.exists():
        print(f"已有 {users.count()} 个监控用户:")
        for user in users:
            status = "🟢 启用" if user.is_active else "🔴 禁用"
            print(f"   {status} @{user.username} - {user.display_name}")
    else:
        print("暂无监控用户")
    
    # 步骤 4: 提供下一步指引
    print("\n📌 下一步操作")
    print("-" * 70)
    print("\n1️⃣  添加监控用户:")
    print("   python manage.py add_twitter_user <username>")
    print("   示例: python manage.py add_twitter_user elonmusk")
    
    print("\n2️⃣  手动监控用户:")
    print("   python manage.py monitor_twitter")
    
    print("\n3️⃣  启动 Django 服务器:")
    print("   python manage.py runserver")
    print("   然后访问: http://localhost:8000/admin/")
    
    print("\n4️⃣  启动自动监控（可选）:")
    print("   # 终端 1: 启动 Redis")
    print("   redis-server")
    print("   ")
    print("   # 终端 2: 启动 Celery Worker")
    print("   celery -A mysite worker -l info")
    print("   ")
    print("   # 终端 3: 启动 Celery Beat")
    print("   celery -A mysite beat -l info")
    
    print("\n" + "=" * 70)
    print("⚠️  重要提示:")
    print("=" * 70)
    print("""
如果无法获取用户信息，可能需要:

1. 升级 Twitter API 访问级别
   - 访问: https://developer.twitter.com/en/portal/products
   - 免费版 API 有严格的限制
   - 建议升级到 Basic ($100/月) 或 Pro 级别

2. 检查 API 权限
   - 确保 App 权限设置为 "Read and Write"
   - 在 Twitter Developer Portal 中检查

3. 使用 OAuth 1.0a 认证（如果有 API Key 和 Secret）
   - 目前使用的是 Bearer Token（只读）
   - OAuth 1.0a 可以提供更多权限

4. 查看 Twitter API 文档
   - https://developer.twitter.com/en/docs/twitter-api
    """)
    
    print("\n💡 提示: 超级用户已创建")
    print("   用户名: admin")
    print("   密码: 请在首次登录时设置")
    print("   访问: http://localhost:8000/admin/")
    
    print("\n" + "=" * 70)
    print("✅ 配置完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
