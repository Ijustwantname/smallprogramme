"""
URL configuration for smallprogram project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app01 import views

urlpatterns = [
    path('api/login/', views.login),

    path('api/register/', views.register),
    path('api/register/send_sms/', views.send_register_sms),

    path('api/banned_user/',  views.banned_user),
    path('api/logout/', views.logout),

    path('api/change_password/', views.change_password),
    path('api/change_password/send_sms/', views.change_password_send_sms),

    path('api/home/user_home/', views.user_home),

    path('api/edit/background/', views.edit_background),
    path('api/edit/profile/', views.edit_profile_image),
    path('api/edit/nickname/', views.edit_nickname),
]