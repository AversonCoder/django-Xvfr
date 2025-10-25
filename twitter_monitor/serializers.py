"""
REST API 序列化器
"""

from rest_framework import serializers
from .models import MonitoredUser, Tweet, Reply, MonitorLog


class MonitoredUserSerializer(serializers.ModelSerializer):
    """监控用户序列化器"""
    tweets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MonitoredUser
        fields = [
            'id', 'username', 'user_id', 'display_name', 'profile_image_url',
            'is_active', 'created_at', 'updated_at', 'last_checked_at', 'tweets_count'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'last_checked_at']
    
    def get_tweets_count(self, obj):
        return obj.tweets.count()


class TweetSerializer(serializers.ModelSerializer):
    """推文序列化器"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_display_name = serializers.CharField(source='author.display_name', read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tweet
        fields = [
            'id', 'tweet_id', 'author', 'author_username', 'author_display_name',
            'tweet_type', 'text', 'created_at', 'retweet_count', 'reply_count',
            'like_count', 'quote_count', 'referenced_tweet_id', 'retweeted_tweet_id',
            'has_media', 'media_urls', 'fetched_at', 'replies_count'
        ]
        read_only_fields = ['fetched_at']
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class ReplySerializer(serializers.ModelSerializer):
    """回复序列化器"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    tweet_text = serializers.CharField(source='tweet.text', read_only=True)
    
    class Meta:
        model = Reply
        fields = [
            'id', 'reply_id', 'tweet', 'tweet_text', 'author', 'author_username',
            'text', 'created_at', 'like_count', 'reply_count', 'fetched_at'
        ]
        read_only_fields = ['fetched_at']


class MonitorLogSerializer(serializers.ModelSerializer):
    """监控日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MonitorLog
        fields = [
            'id', 'user', 'username', 'status', 'tweets_fetched',
            'replies_fetched', 'error_message', 'created_at'
        ]
        read_only_fields = ['created_at']
