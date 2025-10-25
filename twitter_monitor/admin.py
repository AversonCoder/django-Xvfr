from django.contrib import admin
from django.utils.html import format_html
from .models import MonitoredUser, Tweet, Reply, MonitorLog


@admin.register(MonitoredUser)
class MonitoredUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'display_name', 'is_active', 'last_checked_at', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['username', 'display_name', 'user_id']
    readonly_fields = ['user_id', 'created_at', 'updated_at', 'last_checked_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'user_id', 'display_name', 'profile_image_url')
        }),
        ('监控设置', {
            'fields': ('is_active',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'last_checked_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_monitoring', 'disable_monitoring']
    
    def enable_monitoring(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"已启用 {queryset.count()} 个用户的监控")
    enable_monitoring.short_description = "启用监控"
    
    def disable_monitoring(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"已禁用 {queryset.count()} 个用户的监控")
    disable_monitoring.short_description = "禁用监控"


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ['tweet_preview', 'author', 'tweet_type', 'created_at', 'stats_summary', 'has_media']
    list_filter = ['tweet_type', 'has_media', 'created_at', 'author']
    search_fields = ['text', 'tweet_id', 'author__username']
    readonly_fields = ['tweet_id', 'author', 'created_at', 'fetched_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('推文信息', {
            'fields': ('tweet_id', 'author', 'tweet_type', 'text', 'created_at')
        }),
        ('统计数据', {
            'fields': ('retweet_count', 'reply_count', 'like_count', 'quote_count')
        }),
        ('引用信息', {
            'fields': ('referenced_tweet_id', 'retweeted_tweet_id'),
            'classes': ('collapse',)
        }),
        ('媒体信息', {
            'fields': ('has_media', 'media_urls'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('fetched_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tweet_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    tweet_preview.short_description = '推文内容'
    
    def stats_summary(self, obj):
        return format_html(
            '❤️ {} | 🔁 {} | 💬 {} | 📝 {}',
            obj.like_count, obj.retweet_count, obj.reply_count, obj.quote_count
        )
    stats_summary.short_description = '统计'


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['reply_preview', 'author', 'tweet_preview', 'created_at', 'like_count']
    list_filter = ['created_at', 'author']
    search_fields = ['text', 'reply_id', 'author__username']
    readonly_fields = ['reply_id', 'tweet', 'author', 'created_at', 'fetched_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def reply_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    reply_preview.short_description = '回复内容'
    
    def tweet_preview(self, obj):
        return obj.tweet.text[:50] + '...' if len(obj.tweet.text) > 50 else obj.tweet.text
    tweet_preview.short_description = '原推文'


@admin.register(MonitorLog)
class MonitorLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'tweets_fetched', 'replies_fetched', 'created_at']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['user__username', 'error_message']
    readonly_fields = ['user', 'status', 'tweets_fetched', 'replies_fetched', 'error_message', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
