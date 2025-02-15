import uuid
from django.db import models

# Create your models here.



class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    phone = models.CharField(max_length=16)
    password = models.CharField(max_length=64)

class UserImageInfo(models.Model):
    image_data = models.BinaryField(null=True, blank=True)
    background = models.BinaryField(null=True, blank=True)
    user = models.ForeignKey(to='UserInfo', to_field='id',on_delete=models.CASCADE)
    
    

class Blacklist(models.Model):
    token = models.CharField(max_length=255, unique=True)  # 存储Token
    blacklisted_at = models.DateTimeField(auto_now_add=True)  # 添加时间



class ChatSessionMessage(models.Model):
    session_id = models.UUIDField()
    message = models.TextField()
    role = models.CharField(max_length=16)
    create_time = models.DateTimeField(auto_now_add=True)
    type_message = models.CharField(max_length=16, default='text')
    
