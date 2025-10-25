from django.db import models
from django.utils import timezone


class MonitoredUser(models.Model):
    """监控的 Twitter 用户"""
    username = models.CharField(max_length=100, unique=True, verbose_name="用户名")
    user_id = models.CharField(max_length=100, unique=True, verbose_name="用户ID")
    display_name = models.CharField(max_length=200, blank=True, verbose_name="显示名称")
    profile_image_url = models.URLField(blank=True, verbose_name="头像URL")
    is_active = models.BooleanField(default=True, verbose_name="是否启用监控")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    last_checked_at = models.DateTimeField(null=True, blank=True, verbose_name="最后检查时间")
    
    class Meta:
        verbose_name = "监控用户"
        verbose_name_plural = "监控用户"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"@{self.username}"


class Tweet(models.Model):
    """推文"""
    TWEET_TYPE_CHOICES = [
        ('tweet', '原创推文'),
        ('retweet', '转发'),
        ('quote', '引用转发'),
    ]
    
    tweet_id = models.CharField(max_length=100, unique=True, verbose_name="推文ID")
    author = models.ForeignKey(MonitoredUser, on_delete=models.CASCADE, related_name='tweets', verbose_name="作者")
    tweet_type = models.CharField(max_length=20, choices=TWEET_TYPE_CHOICES, default='tweet', verbose_name="推文类型")
    text = models.TextField(verbose_name="推文内容")
    created_at = models.DateTimeField(verbose_name="发布时间")
    
    # 统计数据
    retweet_count = models.IntegerField(default=0, verbose_name="转发数")
    reply_count = models.IntegerField(default=0, verbose_name="回复数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    quote_count = models.IntegerField(default=0, verbose_name="引用数")
    
    # 引用和转发的原推文
    referenced_tweet_id = models.CharField(max_length=100, blank=True, verbose_name="引用推文ID")
    retweeted_tweet_id = models.CharField(max_length=100, blank=True, verbose_name="转发推文ID")
    
    # 媒体
    has_media = models.BooleanField(default=False, verbose_name="包含媒体")
    media_urls = models.JSONField(default=list, blank=True, verbose_name="媒体URL列表")
    
    # 抓取时间
    fetched_at = models.DateTimeField(auto_now_add=True, verbose_name="抓取时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "推文"
        verbose_name_plural = "推文"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['tweet_id']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username}: {self.text[:50]}"


class Reply(models.Model):
    """回复"""
    reply_id = models.CharField(max_length=100, unique=True, verbose_name="回复ID")
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='replies', verbose_name="原推文")
    author = models.ForeignKey(MonitoredUser, on_delete=models.CASCADE, related_name='replies', verbose_name="回复者")
    text = models.TextField(verbose_name="回复内容")
    created_at = models.DateTimeField(verbose_name="回复时间")
    
    # 统计数据
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    reply_count = models.IntegerField(default=0, verbose_name="回复数")
    
    # 抓取时间
    fetched_at = models.DateTimeField(auto_now_add=True, verbose_name="抓取时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "回复"
        verbose_name_plural = "回复"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tweet', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username} 回复 {self.tweet.author.username}"


class MonitorLog(models.Model):
    """监控日志"""
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('partial', '部分成功'),
    ]
    
    user = models.ForeignKey(MonitoredUser, on_delete=models.CASCADE, related_name='logs', verbose_name="监控用户")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="状态")
    tweets_fetched = models.IntegerField(default=0, verbose_name="获取推文数")
    replies_fetched = models.IntegerField(default=0, verbose_name="获取回复数")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "监控日志"
        verbose_name_plural = "监控日志"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.created_at}"
