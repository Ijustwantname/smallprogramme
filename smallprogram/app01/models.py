import uuid
from django.db import models

# Create your models here.

class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    phone = models.CharField(max_length=16)
    password = models.CharField(max_length=64)


"""
    {
        用户名(
            {
                类型:
                数据:
            }
            {
                类型:
                数据:
            }

        ai(
            {
                类型:
                数据:
            }
        )
    }
"""

class Blacklist(models.Model):
    token = models.CharField(max_length=500, unique=True)  # 存储Token
    blacklisted_at = models.DateTimeField(auto_now_add=True)  # 添加时间




class ChatSessionMessage(models.Model):
    session_id = models.UUIDField()
    message = models.TextField()
    role = models.CharField(max_length=16)
    create_time = models.DateTimeField(auto_now_add=True)
    type_message = models.CharField(max_length=16, default='text')
    
