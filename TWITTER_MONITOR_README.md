# Twitter 监控系统 - 使用指南

这是一个基于 Django 的 Twitter 监控系统，可以监控指定 Twitter 用户的推文、回复、转发和评论。

## 功能特性

✅ **监控用户推文** - 自动抓取监控用户的所有推文  
✅ **监控回复** - 抓取监控用户之间的回复互动  
✅ **监控转发** - 记录转发和引用转发  
✅ **定时任务** - 使用 Celery 自动定时抓取  
✅ **REST API** - 提供完整的 RESTful API  
✅ **管理后台** - Django Admin 可视化管理  
✅ **统计分析** - 点赞、转发、回复等数据统计  

---

## 快速开始

### 1. 配置 Twitter API

您需要在 [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) 申请 API 密钥。

#### 获取 Twitter API 密钥步骤：

1. 访问 https://developer.twitter.com/
2. 登录并创建一个应用 (App)
3. 在应用设置中生成 Bearer Token
4. 复制 Bearer Token 备用

#### 设置环境变量：

```bash
# 必需配置
export TWITTER_BEARER_TOKEN="your-bearer-token-here"

# 可选配置 (OAuth 1.0a)
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_SECRET="your-access-secret"

# Redis 配置 (Celery 需要)
export REDIS_URL="redis://localhost:6379/0"
```

**生产环境配置：**

在 Railway 或其他云平台的环境变量中添加以上配置。

---

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

---

### 3. 数据库迁移

```bash
# 执行迁移
python manage.py migrate

# 创建超级用户 (用于访问 Admin)
python manage.py createsuperuser
```

---

### 4. 启动服务

#### 开发环境 (本地):

```bash
# 终端 1: 启动 Django 开发服务器
python manage.py runserver

# 终端 2: 启动 Redis (macOS)
brew install redis
redis-server

# 终端 3: 启动 Celery Worker
celery -A mysite worker -l info

# 终端 4: 启动 Celery Beat (定时任务)
celery -A mysite beat -l info
```

#### 生产环境:

```bash
# 使用 gunicorn 启动 Django
gunicorn mysite.wsgi:application

# 启动 Celery Worker
celery -A mysite worker -l info --detach

# 启动 Celery Beat
celery -A mysite beat -l info --detach
```

---

## 使用方法

### 方法 1: 使用 Django Admin (推荐)

1. 访问 `http://localhost:8000/admin/`
2. 登录管理后台
3. 点击 "监控用户" → "添加监控用户"
4. 输入用户信息并保存
5. 在列表中可以查看推文、回复等数据

### 方法 2: 使用管理命令

```bash
# 添加监控用户
python manage.py add_twitter_user elonmusk
python manage.py add_twitter_user openai

# 立即监控指定用户
python manage.py monitor_twitter elonmusk

# 监控所有用户
python manage.py monitor_twitter
```

### 方法 3: 使用 REST API

#### 添加监控用户

```bash
curl -X POST http://localhost:8000/twitter/api/monitored-users/add_user/ \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk"}'
```

#### 获取监控用户列表

```bash
curl http://localhost:8000/twitter/api/monitored-users/
```

#### 立即监控指定用户

```bash
curl -X POST http://localhost:8000/twitter/api/monitored-users/1/monitor_now/
```

#### 获取推文列表

```bash
# 所有推文
curl http://localhost:8000/twitter/api/tweets/

# 指定用户的推文
curl http://localhost:8000/twitter/api/tweets/?author=1

# 搜索推文
curl http://localhost:8000/twitter/api/tweets/?search=python

# 按类型筛选
curl http://localhost:8000/twitter/api/tweets/?tweet_type=retweet
```

#### 获取回复列表

```bash
# 所有回复
curl http://localhost:8000/twitter/api/replies/

# 指定推文的回复
curl http://localhost:8000/twitter/api/tweets/1/replies/
```

#### 查看监控日志

```bash
curl http://localhost:8000/twitter/api/logs/
```

---

## API 文档

### 监控用户 API

- `GET /twitter/api/monitored-users/` - 获取监控用户列表
- `POST /twitter/api/monitored-users/` - 创建监控用户
- `GET /twitter/api/monitored-users/{id}/` - 获取单个用户详情
- `PUT /twitter/api/monitored-users/{id}/` - 更新用户
- `DELETE /twitter/api/monitored-users/{id}/` - 删除用户
- `POST /twitter/api/monitored-users/add_user/` - 通过用户名添加用户
- `POST /twitter/api/monitored-users/{id}/monitor_now/` - 立即监控
- `POST /twitter/api/monitored-users/monitor_all/` - 监控所有用户

### 推文 API

- `GET /twitter/api/tweets/` - 获取推文列表
- `GET /twitter/api/tweets/{id}/` - 获取推文详情
- `GET /twitter/api/tweets/{id}/replies/` - 获取推文的回复

**查询参数：**
- `author` - 按作者 ID 筛选
- `tweet_type` - 按类型筛选 (tweet/retweet/quote)
- `has_media` - 是否包含媒体
- `search` - 搜索推文内容
- `ordering` - 排序字段 (-created_at, -like_count 等)

### 回复 API

- `GET /twitter/api/replies/` - 获取回复列表
- `GET /twitter/api/replies/{id}/` - 获取回复详情

### 监控日志 API

- `GET /twitter/api/logs/` - 获取监控日志列表
- `GET /twitter/api/logs/{id}/` - 获取日志详情

---

## 定时任务配置

系统默认配置了以下定时任务（在 `mysite/celery.py` 中）：

```python
# 每30分钟监控一次所有用户
'monitor-all-users-every-30-minutes': {
    'task': 'twitter_monitor.tasks.monitor_all_users_task',
    'schedule': crontab(minute='*/30'),
},

# 每天凌晨3点清理30天前的旧数据
'cleanup-old-data-daily': {
    'task': 'twitter_monitor.tasks.cleanup_old_data_task',
    'schedule': crontab(hour=3, minute=0),
    'kwargs': {'days': 30},
},
```

修改定时任务频率：
- 修改 `mysite/celery.py` 中的 `crontab` 参数
- 重启 Celery Beat 服务

---

## 数据库模型

### MonitoredUser (监控用户)
- `username` - Twitter 用户名
- `user_id` - Twitter 用户 ID
- `display_name` - 显示名称
- `is_active` - 是否启用监控

### Tweet (推文)
- `tweet_id` - 推文 ID
- `author` - 作者 (外键)
- `tweet_type` - 类型 (tweet/retweet/quote)
- `text` - 推文内容
- `retweet_count`, `reply_count`, `like_count` - 统计数据
- `has_media`, `media_urls` - 媒体信息

### Reply (回复)
- `reply_id` - 回复 ID
- `tweet` - 原推文 (外键)
- `author` - 回复者 (外键)
- `text` - 回复内容

### MonitorLog (监控日志)
- `user` - 监控用户 (外键)
- `status` - 状态 (success/failed/partial)
- `tweets_fetched` - 获取的推文数
- `error_message` - 错误信息

---

## 故障排查

### 1. Twitter API 错误

**错误：** "TWITTER_BEARER_TOKEN 未配置"

**解决：** 确保已设置环境变量 `TWITTER_BEARER_TOKEN`

```bash
export TWITTER_BEARER_TOKEN="your-token"
```

### 2. Celery 连接错误

**错误：** "Error connecting to Redis"

**解决：** 
1. 确保 Redis 已启动：`redis-server`
2. 检查 Redis URL 配置：`echo $REDIS_URL`

### 3. 推文获取失败

**可能原因：**
- Twitter API 限流 (tweepy 会自动等待)
- 用户账号被保护
- 用户不存在

**解决：** 查看监控日志了解详细错误信息

### 4. 数据库错误

**错误：** "KeyError: 'PGDATABASE'"

**解决：** 开发环境会自动使用 SQLite，确保已运行 `python manage.py migrate`

---

## 高级配置

### 修改抓取频率

编辑 `mysite/celery.py`:

```python
# 每小时执行一次
'schedule': crontab(minute=0),

# 每6小时执行一次  
'schedule': crontab(minute=0, hour='*/6'),

# 每天早上9点执行
'schedule': crontab(hour=9, minute=0),
```

### 增加抓取数量

编辑 `twitter_monitor/services.py` 中的 `monitor_user` 方法：

```python
# 默认每次最多获取 100 条推文
tweets = self.twitter_service.fetch_user_tweets(
    user_id=user.user_id,
    max_results=100,  # 修改这个值 (5-100)
    since_id=since_id
)
```

### 数据保留时长

在定时任务中修改保留天数：

```python
'kwargs': {'days': 60},  # 保留 60 天数据
```

---

## 项目结构

```
django-Xvfr/
├── mysite/                 # Django 项目配置
│   ├── settings.py         # 项目设置
│   ├── urls.py             # 主路由
│   ├── celery.py           # Celery 配置
│   └── wsgi.py             # WSGI 配置
├── twitter_monitor/        # Twitter 监控应用
│   ├── models.py           # 数据模型
│   ├── admin.py            # Admin 配置
│   ├── services.py         # Twitter API 服务
│   ├── tasks.py            # Celery 任务
│   ├── views.py            # API 视图
│   ├── serializers.py      # API 序列化器
│   ├── urls.py             # 路由配置
│   └── management/         # 管理命令
│       └── commands/
│           ├── add_twitter_user.py
│           └── monitor_twitter.py
├── requirements.txt        # 依赖包
├── manage.py               # Django 管理脚本
└── TWITTER_MONITOR_README.md  # 本文档
```

---

## 技术栈

- **Django 5.2.7** - Web 框架
- **Django REST Framework** - REST API
- **Tweepy 4.16.0** - Twitter API 客户端
- **Celery 5.5.3** - 异步任务队列
- **Redis** - 消息代理
- **PostgreSQL / SQLite** - 数据库

---

## 注意事项

⚠️ **Twitter API 限制**
- 免费版 API 有访问频率限制
- 某些功能需要付费 API 计划
- 建议合理设置监控频率

⚠️ **隐私和法律**
- 仅监控公开的推文
- 遵守 Twitter 使用条款
- 不要滥用 API

⚠️ **性能优化**
- 监控用户不宜过多 (建议 < 100)
- 定期清理旧数据
- 生产环境建议使用 PostgreSQL

---

## 许可证

本项目基于 Django 框架开发，遵循相应的开源许可证。

---

## 支持

如有问题，请查看：
- [Django 文档](https://docs.djangoproject.com/)
- [Tweepy 文档](https://docs.tweepy.org/)
- [Celery 文档](https://docs.celeryproject.org/)
