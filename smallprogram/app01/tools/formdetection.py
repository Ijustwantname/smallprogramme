import re
from django import forms
from app01.models import UserInfo
from django.core.validators import RegexValidator
from app01.tools.encrypt import encrypt_password
from django.core.cache import cache

class UserChangePasswordModelForm(forms.ModelForm):
    password_confirm = forms.CharField(label='确认密码')
    phone = forms.CharField(label='找到验证码')
    send_sms = forms.CharField(label='发送短信验证码')
    class Meta:
        model = UserInfo
        fields = ['password', 'password_confirm', 'phone', 'send_sms']
    


    def clean_password(self):
        password = self.cleaned_data.get('password')

        pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?/~`-]).{8,12}$'
        if not re.fullmatch(pattern, password):
            raise forms.ValidationError('格式错误, 密码必须包含至少一个数字、一个小写字母、一个大写字母和一个特殊符号(如!@#$%^&*等)且长度为8-12位。')

        return encrypt_password(password)
    

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        password_confirm = encrypt_password(password_confirm)

        if password != password_confirm:
            raise forms.ValidationError('两次输入的密码不一致')
        
        return password_confirm
    
    def clean_send_sms(self):
        print(self.cleaned_data)
        send_sms = self.cleaned_data.get('send_sms')
        print('send_sms:', send_sms)

        

        cache_send_sms = cache.get(f'sms_code_change_password_{self.cleaned_data.get("phone")}')
        print('cache_send_sms:', cache_send_sms)
        print('phone:', self.cleaned_data.get('phone'))

        if not cache_send_sms:
            raise forms.ValidationError('验证码过期')
        
        if send_sms != cache_send_sms:
            
            raise forms.ValidationError('验证码错误')

        return send_sms

    



class UserRegisterModelForm(forms.ModelForm):
    password_confirm = forms.CharField(label='确认密码')
    send_sms = forms.CharField(label='发送短信验证码')

    class Meta:
        model = UserInfo
        fields = ['username', 'phone', 'password', 'password_confirm', 'send_sms']



    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5 or len(username) > 10:
            raise forms.ValidationError('用户名长度必须在5-10个字符之间')
        
        return username


    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        ret: bool = UserInfo.objects.filter(phone=phone).exists()
        if ret:
            raise forms.ValidationError('手机号码已被注册')

        pattern = r'^1[3-9]\d{9}$'
        if not re.fullmatch(pattern, phone):
            raise forms.ValidationError('手机号码格式错误')
        
        return phone
    

    def clean_password(self):
        password = self.cleaned_data.get('password')

        pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?/~`-]).{8,12}$'
        if not re.fullmatch(pattern, password):
            raise forms.ValidationError('格式错误, 密码必须包含至少一个数字、一个小写字母、一个大写字母和一个特殊符号(如!@#$%^&*等)且长度为8-12位。')

        return encrypt_password(password)
    

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        password_confirm = encrypt_password(password_confirm)

        if password != password_confirm:
            raise forms.ValidationError('两次输入的密码不一致')
        
        return password_confirm
    
    def clean_send_sms(self):
        send_sms = self.cleaned_data.get('send_sms')
        
        cache_send_sms = cache.get(f'sms_code_{self.cleaned_data.get("phone")}')


        if not cache_send_sms:
            raise forms.ValidationError('验证码过期')
        
        if send_sms != cache_send_sms:
            
            raise forms.ValidationError('验证码错误')

        return send_sms





class UserSendSmsModelForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^1[3-9]\d{9}$'
        if not re.fullmatch(pattern, phone):
            raise forms.ValidationError('手机号码格式错误')
        return phone






class UserLoginModelForm(forms.ModelForm):

    class Meta:
        model = UserInfo
        fields = ['phone', 'password']
    

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^1[3-9]\d{9}$'
        if not re.fullmatch(pattern, phone):
            raise forms.ValidationError('手机号码格式错误')
        return phone
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?/~`-]).{8,12}$'
        if not re.fullmatch(pattern, password):
            raise forms.ValidationError('格式错误, 密码必须包含至少一个数字、一个小写字母、一个大写字母和一个特殊符号(如!@#$%^&*等)且长度为8-12位。')

        return encrypt_password(password)


        


