from django.db import models


# Create your models here.
from user.models import User


class Message(models.Model):
    messages_type = (
        ('unread', '未读'),
        ('done', '已读'),
        ('saved', '收藏'),
    )
    message_type = models.CharField(max_length=32, choices=messages_type, default='未读')
    title = models.CharField(max_length=64)
    content = models.CharField(max_length=500)
    c_time = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_message'
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name
