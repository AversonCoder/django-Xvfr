# Django Twitter 监控系统

一个功能完整的 Twitter 监控系统,可以监控指定用户的推文、回复、转发和评论。

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/GB6Eki?referralCode=U5zXSw)

## ✨ 功能特性

- 🔍 **监控推文** - 自动抓取监控用户的所有推文
- 💬 **监控回复** - 记录用户之间的回复互动
- 🔁 **监控转发** - 识别转发和引用转发
- ⏰ **定时任务** - 使用 Celery 自动定时抓取
- 🌐 **REST API** - 完整的 RESTful API 接口
- 🎛️ **管理后台** - Django Admin 可视化管理
- 📊 **统计分析** - 点赞、转发、回复等数据统计

## 🚀 快速开始

### 1. 获取 Twitter API 密钥

访问 [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) 创建应用并获取 Bearer Token。

### 2. 配置环境变量

```bash
export TWITTER_BEARER_TOKEN="your-bearer-token"
export REDIS_URL="redis://localhost:6379/0"
```

### 3. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. 启动服务

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

### 6. 添加监控用户

```bash
python manage.py add_twitter_user Twitter
python manage.py monitor_twitter
```

## 📚 文档

- 📖 [完整使用文档](TWITTER_MONITOR_README.md)
- 🚀 [快速开始指南](快速开始.md)
- 📝 [项目总结](项目总结.md)

## 🔧 技术栈

- Django 5.2.7 - Web 框架
- Django REST Framework - REST API
- Tweepy 4.16.0 - Twitter API 客户端
- Celery 5.5.3 - 异步任务队列
- Redis 7.0.0 - 消息代理
- PostgreSQL / SQLite - 数据库

## 🌐 API 接口

- `GET /twitter/api/monitored-users/` - 监控用户列表
- `GET /twitter/api/tweets/` - 推文列表
- `GET /twitter/api/replies/` - 回复列表
- `POST /twitter/api/monitored-users/add_user/` - 添加监控用户
- `POST /twitter/api/monitored-users/{id}/monitor_now/` - 立即监控

访问 http://localhost:8000/admin/ 查看管理后台。

## 📦 项目结构

```
django-Xvfr/
├── mysite/                 # Django 项目配置
│   ├── settings.py         # 项目设置
│   ├── celery.py          # Celery 配置
│   └── urls.py            # 路由配置
├── twitter_monitor/       # Twitter 监控应用
│   ├── models.py          # 数据模型
│   ├── services.py        # Twitter API 服务
│   ├── tasks.py           # Celery 任务
│   ├── views.py           # API 视图
│   └── admin.py           # Admin 配置
├── requirements.txt       # 依赖包
└── manage.py             # Django 管理脚本
```

## 🧪 测试

运行测试脚本：

```bash
python test_twitter_monitor.py
```

## 📝 License

MIT License
