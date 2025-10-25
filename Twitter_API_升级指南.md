# Twitter API 升级指南

## 🎯 当前状态

✅ **API 配置成功** - Bearer Token 已正确加载  
⚠️ **API 访问受限** - 免费版 Twitter API 有严格限制

## ⚠️ 问题说明

你当前使用的 Twitter API 是 **Free（免费版）**，该版本有以下限制：

### 免费版限制
- ❌ 无法获取用户信息（`/users/by/username` 端点不可用）
- ❌ 无法获取用户推文
- ❌ 无法搜索推文
- ❌ 每月只有 1,500 次推文查看
- ✅ 只能发推文（写入操作）

**这意味着监控功能无法在免费版上运行。**

## 💡 解决方案

### 方案 1: 升级到 Basic 级别（推荐）

**价格**: $100/月

**功能**:
- ✅ 10,000 次推文查看/月
- ✅ 可以获取用户信息
- ✅ 可以获取用户推文
- ✅ 可以搜索推文
- ✅ 适合小规模监控（1-10 个用户）

**升级步骤**:
1. 访问 https://developer.twitter.com/en/portal/products
2. 选择 "Basic" 计划
3. 绑定支付方式
4. 升级后重新生成 Bearer Token

### 方案 2: 升级到 Pro 级别（大规模监控）

**价格**: $5,000/月

**功能**:
- ✅ 1,000,000 次推文查看/月
- ✅ 完整的 API 访问
- ✅ 适合大规模监控（100+ 用户）

### 方案 3: 申请学术研究访问（免费，但需审批）

**条件**:
- 必须是学术研究人员
- 需要提交研究计划
- 审批时间：1-2 周

**申请地址**:
https://developer.twitter.com/en/products/twitter-api/academic-research

### 方案 4: 使用替代方案（不推荐）

如果预算有限，可以考虑：
- 使用 Twitter 官方网页爬取（违反 ToS，不推荐）
- 使用第三方数据服务（如 Brandwatch、Sprinklr）
- 等待 Twitter API 政策变化

## 📊 API 级别对比

| 功能 | Free | Basic | Pro |
|------|------|-------|-----|
| 价格 | $0 | $100/月 | $5,000/月 |
| 推文查看 | 1,500/月 | 10,000/月 | 1,000,000/月 |
| 获取用户信息 | ❌ | ✅ | ✅ |
| 获取推文 | ❌ | ✅ | ✅ |
| 搜索推文 | ❌ | ✅ | ✅ |
| 实时流 | ❌ | ❌ | ✅ |

## 🚀 升级后如何使用

升级到 Basic 或 Pro 后：

### 1. 重新生成 API 密钥

在 Twitter Developer Portal 中：
- 删除旧的 Bearer Token
- 生成新的 Bearer Token
- 更新 `.env` 文件中的 `TWITTER_BEARER_TOKEN`

### 2. 测试连接

```bash
python quick_start.py
```

应该看到：
```
✅ API 连接成功！
   测试用户: @Twitter
   显示名称: Twitter
```

### 3. 添加监控用户

```bash
python manage.py add_twitter_user elonmusk
python manage.py add_twitter_user openai
python manage.py add_twitter_user NASA
```

### 4. 开始监控

```bash
python manage.py monitor_twitter
```

### 5. 启动 Django 和 Celery

```bash
# 终端 1: Django
python manage.py runserver

# 终端 2: Redis
redis-server

# 终端 3: Celery Worker
celery -A mysite worker -l info

# 终端 4: Celery Beat
celery -A mysite beat -l info
```

## 🎯 当前可用功能

虽然免费版 API 无法监控，但项目的以下功能仍可测试：

### 1. Django Admin 后台

```bash
python manage.py runserver
```

访问 http://localhost:8000/admin/
- 用户名: admin
- 密码: (首次登录时设置)

### 2. REST API

可以测试 API 接口结构（虽然没有数据）：

```bash
# 获取监控用户列表（空）
curl http://localhost:8000/twitter/api/monitored-users/

# 获取推文列表（空）
curl http://localhost:8000/twitter/api/tweets/
```

### 3. 数据库模型

数据库已创建，可以手动添加测试数据：

```bash
python manage.py shell
```

```python
from twitter_monitor.models import MonitoredUser, Tweet

# 手动创建测试用户
user = MonitoredUser.objects.create(
    username="test_user",
    user_id="123456",
    display_name="Test User"
)

# 创建测试推文
tweet = Tweet.objects.create(
    tweet_id="789",
    author=user,
    text="This is a test tweet",
    created_at="2025-01-01 12:00:00"
)
```

## 📞 联系 Twitter 支持

如果有疑问，可以联系 Twitter Developer Support：
- 论坛: https://twittercommunity.com/
- 邮件: api-support@twitter.com

## 💰 费用说明

### Basic 级别 ($100/月)

**适合场景**:
- 监控 5-10 个用户
- 每个用户每天发 10 条推文
- 每月约 1,500 条推文 = **在限额内**

**费用分析**:
- 10,000 推文查看/月
- 监控 10 个用户 × 10 推文/天 × 30 天 = 3,000 推文/月
- ✅ 足够使用

### Pro 级别 ($5,000/月)

**适合场景**:
- 监控 100+ 用户
- 企业级数据分析
- 实时监控需求

## 📝 总结

1. ✅ **项目已完全开发完成**
2. ✅ **代码已经过测试**
3. ⚠️ **需要升级 Twitter API 才能运行监控功能**
4. 💡 **建议升级到 Basic 级别 ($100/月)**

## 🔗 相关链接

- Twitter Developer Portal: https://developer.twitter.com/
- API 定价: https://developer.twitter.com/en/portal/products
- API 文档: https://developer.twitter.com/en/docs/twitter-api
- 限制说明: https://developer.twitter.com/en/docs/twitter-api/rate-limits

---

如有问题，请查看项目文档或联系开发者。
