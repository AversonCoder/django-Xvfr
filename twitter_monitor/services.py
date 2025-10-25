"""
Twitter API 服务模块

使用 Tweepy 库与 Twitter API v2 交互
需要在 Django settings 中配置以下环境变量:
- TWITTER_BEARER_TOKEN
- TWITTER_API_KEY (可选)
- TWITTER_API_SECRET (可选)
- TWITTER_ACCESS_TOKEN (可选)
- TWITTER_ACCESS_SECRET (可选)
"""

import tweepy
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import MonitoredUser, Tweet, Reply, MonitorLog

logger = logging.getLogger(__name__)


class TwitterService:
    """Twitter API 服务类"""
    
    def __init__(self):
        """初始化 Twitter API 客户端"""
        # 使用 Bearer Token 进行认证 (只读访问)
        bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', None)
        
        if not bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN 未配置")
        
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            wait_on_rate_limit=True
        )
    
    def get_user_by_username(self, username):
        """
        根据用户名获取 Twitter 用户信息
        
        Args:
            username: Twitter 用户名 (不带 @)
            
        Returns:
            dict: 用户信息字典
        """
        try:
            response = self.client.get_user(
                username=username,
                user_fields=['id', 'name', 'username', 'profile_image_url', 'created_at']
            )
            
            if response.data:
                user = response.data
                return {
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': user.name,
                    'profile_image_url': user.profile_image_url or '',
                }
            return None
        except Exception as e:
            logger.error(f"获取用户信息失败 @{username}: {str(e)}")
            return None
    
    def fetch_user_tweets(self, user_id, max_results=100, since_id=None):
        """
        获取用户的推文
        
        Args:
            user_id: Twitter 用户 ID
            max_results: 最多获取的推文数量 (5-100)
            since_id: 只获取此 ID 之后的推文
            
        Returns:
            list: 推文列表
        """
        try:
            tweets = []
            
            # 获取推文
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                since_id=since_id,
                tweet_fields=[
                    'id', 'text', 'created_at', 'public_metrics', 
                    'referenced_tweets', 'attachments'
                ],
                expansions=['attachments.media_keys'],
                media_fields=['url', 'preview_image_url']
            )
            
            if not response.data:
                return tweets
            
            # 处理媒体信息
            media_dict = {}
            if response.includes and 'media' in response.includes:
                for media in response.includes['media']:
                    media_dict[media.media_key] = {
                        'url': media.url if hasattr(media, 'url') else media.preview_image_url,
                        'type': media.type
                    }
            
            for tweet in response.data:
                tweet_data = self._parse_tweet(tweet, media_dict)
                tweets.append(tweet_data)
            
            return tweets
            
        except Exception as e:
            logger.error(f"获取用户推文失败 {user_id}: {str(e)}")
            return []
    
    def fetch_tweet_replies(self, tweet_id, max_results=100):
        """
        获取推文的回复
        
        Args:
            tweet_id: 推文 ID
            max_results: 最多获取的回复数量
            
        Returns:
            list: 回复列表
        """
        try:
            replies = []
            
            # 使用搜索 API 查找回复
            query = f"conversation_id:{tweet_id}"
            
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['id', 'text', 'created_at', 'public_metrics', 'author_id'],
            )
            
            if not response.data:
                return replies
            
            for reply in response.data:
                if reply.id != tweet_id:  # 排除原推文
                    reply_data = {
                        'reply_id': reply.id,
                        'author_id': reply.author_id,
                        'text': reply.text,
                        'created_at': reply.created_at,
                        'like_count': reply.public_metrics.get('like_count', 0) if reply.public_metrics else 0,
                        'reply_count': reply.public_metrics.get('reply_count', 0) if reply.public_metrics else 0,
                    }
                    replies.append(reply_data)
            
            return replies
            
        except Exception as e:
            logger.error(f"获取推文回复失败 {tweet_id}: {str(e)}")
            return []
    
    def _parse_tweet(self, tweet, media_dict=None):
        """解析推文数据"""
        tweet_type = 'tweet'
        referenced_tweet_id = ''
        retweeted_tweet_id = ''
        
        # 判断推文类型
        if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
            ref = tweet.referenced_tweets[0]
            if ref.type == 'retweeted':
                tweet_type = 'retweet'
                retweeted_tweet_id = ref.id
            elif ref.type == 'quoted':
                tweet_type = 'quote'
                referenced_tweet_id = ref.id
        
        # 处理媒体
        media_urls = []
        has_media = False
        if media_dict and hasattr(tweet, 'attachments') and tweet.attachments:
            if 'media_keys' in tweet.attachments:
                has_media = True
                for key in tweet.attachments['media_keys']:
                    if key in media_dict:
                        media_urls.append(media_dict[key]['url'])
        
        return {
            'tweet_id': tweet.id,
            'tweet_type': tweet_type,
            'text': tweet.text,
            'created_at': tweet.created_at,
            'retweet_count': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
            'reply_count': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
            'like_count': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
            'quote_count': tweet.public_metrics.get('quote_count', 0) if tweet.public_metrics else 0,
            'referenced_tweet_id': referenced_tweet_id,
            'retweeted_tweet_id': retweeted_tweet_id,
            'has_media': has_media,
            'media_urls': media_urls,
        }


class TwitterMonitorService:
    """Twitter 监控服务类"""
    
    def __init__(self):
        self.twitter_service = TwitterService()
    
    def add_monitored_user(self, username):
        """
        添加监控用户
        
        Args:
            username: Twitter 用户名 (不带 @)
            
        Returns:
            MonitoredUser: 监控用户对象, 或 None
        """
        # 获取用户信息
        user_info = self.twitter_service.get_user_by_username(username)
        if not user_info:
            logger.error(f"无法找到用户: @{username}")
            return None
        
        # 创建或更新监控用户
        user, created = MonitoredUser.objects.update_or_create(
            username=username,
            defaults=user_info
        )
        
        if created:
            logger.info(f"添加监控用户: @{username}")
        else:
            logger.info(f"更新监控用户: @{username}")
        
        return user
    
    def monitor_user(self, user):
        """
        监控单个用户的推文和回复
        
        Args:
            user: MonitoredUser 对象
            
        Returns:
            dict: 监控结果统计
        """
        if not user.is_active:
            logger.info(f"用户 @{user.username} 监控已禁用")
            return {'tweets': 0, 'replies': 0, 'status': 'disabled'}
        
        tweets_count = 0
        replies_count = 0
        error_message = ''
        
        try:
            # 获取最新推文 ID (用于增量获取)
            latest_tweet = user.tweets.order_by('-created_at').first()
            since_id = latest_tweet.tweet_id if latest_tweet else None
            
            # 获取用户推文
            tweets = self.twitter_service.fetch_user_tweets(
                user_id=user.user_id,
                max_results=100,
                since_id=since_id
            )
            
            # 保存推文
            for tweet_data in tweets:
                tweet, created = Tweet.objects.update_or_create(
                    tweet_id=tweet_data['tweet_id'],
                    defaults={
                        'author': user,
                        **tweet_data
                    }
                )
                if created:
                    tweets_count += 1
                    
                    # 获取推文的回复 (只对新推文)
                    replies = self.twitter_service.fetch_tweet_replies(
                        tweet_id=tweet_data['tweet_id'],
                        max_results=50
                    )
                    
                    # 保存回复
                    for reply_data in replies:
                        # 查找回复作者 (可能是监控用户)
                        try:
                            reply_author = MonitoredUser.objects.get(user_id=reply_data['author_id'])
                        except MonitoredUser.DoesNotExist:
                            # 如果回复者不是监控用户,跳过
                            continue
                        
                        reply, reply_created = Reply.objects.update_or_create(
                            reply_id=reply_data['reply_id'],
                            defaults={
                                'tweet': tweet,
                                'author': reply_author,
                                'text': reply_data['text'],
                                'created_at': reply_data['created_at'],
                                'like_count': reply_data['like_count'],
                                'reply_count': reply_data['reply_count'],
                            }
                        )
                        if reply_created:
                            replies_count += 1
            
            # 更新最后检查时间
            user.last_checked_at = timezone.now()
            user.save()
            
            # 记录日志
            MonitorLog.objects.create(
                user=user,
                status='success',
                tweets_fetched=tweets_count,
                replies_fetched=replies_count,
            )
            
            logger.info(f"监控用户 @{user.username} 完成: {tweets_count} 推文, {replies_count} 回复")
            
            return {
                'tweets': tweets_count,
                'replies': replies_count,
                'status': 'success'
            }
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"监控用户 @{user.username} 失败: {error_message}")
            
            # 记录错误日志
            MonitorLog.objects.create(
                user=user,
                status='failed',
                tweets_fetched=tweets_count,
                replies_fetched=replies_count,
                error_message=error_message,
            )
            
            return {
                'tweets': tweets_count,
                'replies': replies_count,
                'status': 'failed',
                'error': error_message
            }
    
    def monitor_all_users(self):
        """
        监控所有启用的用户
        
        Returns:
            dict: 总体监控结果
        """
        users = MonitoredUser.objects.filter(is_active=True)
        
        total_tweets = 0
        total_replies = 0
        success_count = 0
        failed_count = 0
        
        for user in users:
            result = self.monitor_user(user)
            total_tweets += result.get('tweets', 0)
            total_replies += result.get('replies', 0)
            
            if result.get('status') == 'success':
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(
            f"批量监控完成: {success_count} 成功, {failed_count} 失败, "
            f"{total_tweets} 推文, {total_replies} 回复"
        )
        
        return {
            'total_users': users.count(),
            'success': success_count,
            'failed': failed_count,
            'total_tweets': total_tweets,
            'total_replies': total_replies,
        }
