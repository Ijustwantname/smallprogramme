import json
from django.http import JsonResponse
from django.shortcuts import render
from app01.tools import encrypt
from app01.tools import formdetection
from app01.models import UserInfo
from app01.tools import tokenjwt
from app01.tools import utilityfunc
from django.core.cache import cache
from app01.sms import sendsms
from app01.models import Blacklist



# Create your views here.

''' receive data from front-end
    json = {
        phone: 'phone',
        password: 'password'
    }

'''

''' send data to front-end
    
'''




def login(request):
    
    if request.method == 'POST':
        # 接收前端数据
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            password = data.get('password')
        except json.JSONDecodeError:
            send_json = {  
                'code': 400, 
                'msg': 'json格式错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=400)


        # 表单信息查验
        model = formdetection.UserLoginModelForm(data=data)
        if not model.is_valid():
            error_dirt = {field: error[0] for field, error in model.errors.items()}
            send_json = {  
                'code': 422, 
                'msg': 'form error',
                'data': error_dirt,
            }
            return JsonResponse(data=send_json, status=422)
        
        # 用户信息查询  
        user_info = UserInfo.objects.filter(phone=phone).first()
        if not user_info:
            send_json = {  
                'code': 404, 
                'msg': '用户不存在',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=404)

        # 密码加密验证
        if encrypt.encrypt_password(password) == user_info.password:
            jwt_token = tokenjwt.generate_token(user_info.id)

            send_json = {  
                'code': 200, 
                'msg': '登录成功',  
                'data': {
                    'token': jwt_token,
                    'user_id': user_info.id,
                    'url_redirect': '/home_page/'
                    }
            
            }
                    
            return JsonResponse(data=send_json, status=200)
        
        # 密码错误
        else:
            send_json = {  
                'code': 401, 
                'msg': '密码错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=401)


def send_register_sms(request):
    if request.method == 'POST':
        # 接收前端数据
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
        except json.JSONDecodeError:
            send_json = {  
                'code': 400, 
                'msg': 'json格式错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=400)

        # 表单信息查验
        modelform = formdetection.UserSendSmsModelForm(data=data)
        if not modelform.is_valid():
            error_dirt = {field: error[0] for field, error in modelform.errors.items()}
            send_json = {  
                'code': 422, 
                'msg': 'json format error',
                'data': error_dirt,
            }
            return JsonResponse(data=send_json, status=422)
        
        # 验证码发送频率限制
        if cache.get(f'sms_cooldown_{phone}'):
            send_json = {  
                'code': 429, 
                'msg': '发送频率过快',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=429)
        
        # 生成验证码
        sms = utilityfunc.random_string()
        cache.set(f'sms_code_{phone}', sms, timeout=300)


        # 发送验证码
        sendsms.send_sms(phone, sms)

        cache.set(f'sms_cooldown_{phone}', True, timeout=60)


        send_json = {  
            'code': 200, 
            'msg': '验证码发送成功',  
            'data': {},   
            }
        
        return JsonResponse(data=send_json, status=200)



def register(request):
    if request.method == 'POST':
        # 接收前端数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            send_json = {  
                'code': 400, 
                'msg': '数据格式错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=400) 
        
        # 表单信息查验
        modelform = formdetection.UserRegisterModelForm(data=data)

        if not modelform.is_valid():
            error_dirt = {field: error[0] for field, error in modelform.errors.items()}
            send_json = {  
                'code': 409,
                'msg': '注册失败',
                'data': error_dirt,
                }
            return JsonResponse(data=send_json, status=409)
        

        modelform.save()

        send_json = {  
            'code': 200, 
            'msg': '注册成功',  
            'data': {},   
            }
        return JsonResponse(data=send_json, status=200)
        

def banned_user(request):
    if request.method == 'POST':
        # 接收中间件信息
        user_id = request.user_id  # 这里需要从token中获取用户id
        data = json.loads(request.body)
        user_pwd = data.get('password')
        encrypted_pwd = encrypt.encrypt_password(user_pwd)

            
        # 获取密码
        row_obj = UserInfo.objects.filter(id=user_id).first()

        if encrypted_pwd != row_obj.password:
            send_json = {  
                'code': 401, 
                'msg': '用户身份验证失败, 密码错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=401)

    
        Blacklist.objects.create(token=request.token)
        

        UserInfo.objects.filter(id=user_id).delete()
        send_json = {  
            'code': 200, 
            'msg': '用户已删除',  
            'data': {},   
            }
        
        return JsonResponse(data=send_json, status=200)


def logout(request):
    token = request.token
    Blacklist.objects.create(token=token)


    send_json = {   
        'code': 200, 
        'msg': '退出成功',  
        'data': {
            'url_redirect': '/login/'
        },   
    }
    
    return JsonResponse(data=send_json, status=200)


def change_password_send_sms(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        user_phone = data.get('phone')

        # 表单信息查验
        modelform = formdetection.UserSendSmsModelForm(data=data)
        if not modelform.is_valid():
            error_dirt = {field: error[0] for field, error in modelform.errors.items()}
            send_json = {  
                'code': 422, 
                'msg': 'json format error',
                'data': error_dirt,
            }
            return JsonResponse(data=send_json, status=422)
        

        # 是否存在该用户
        exist = UserInfo.objects.filter(phone=user_phone).exists()
        if not exist:
            send_json = {  
                'code': 404, 
                'msg': '用户不存在, 请输入正确的手机号',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=404)



        # 验证码发送频率限制
        if cache.get(f'sms_cooldown_change_password_{user_phone}'):
            send_json = {  
                'code': 429, 
                'msg': '发送频率过快',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=429)
        

        sms = utilityfunc.random_string()
        cache.set(f'sms_code_change_password_{user_phone}', sms, timeout=300)

        sendsms.send_sms(user_phone, sms)

        cache.set(f'sms_cooldown_change_password_{user_phone}', True, timeout=60)

        send_json = {  
            'code': 200, 
            'msg': '验证码发送成功',  
            'data': {},   
            }
        
        return JsonResponse(data=send_json, status=200)
        





def change_password(request):
    if request.method == 'POST':
        # 接收前端数据
        try:
            data = json.loads(request.body)
            user_phone = data.get('phone')

        except json.JSONDecodeError:
            send_json = {  
                'code': 400, 
                'msg': '数据格式错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=400) 
 
        # 表单信息查验

        obj_row = UserInfo.objects.filter(phone=user_phone).first()


        modelform = formdetection.UserChangePasswordModelForm(data=data, instance=obj_row)

        if not modelform.is_valid():
            error_dirt = {field: error[0] for field, error in modelform.errors.items()}
            send_json = {  
                'code': 400,
                'msg': '修改密码失败',
                'data': error_dirt,
                }
            return JsonResponse(data=send_json, status=400)
        

        instance = modelform.save(commit=False)
        instance.save(update_fields=['password'])

        data_json = {
            'code': 200,
            'msg': '修改密码成功',
            'data': {},
            }
        return JsonResponse(data=data_json, status=200)

        



'''
data = {
    "image_data": {
        "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "filename": "avatar.png",
        "type": "image/png"
    },
    "user_id": 12345,
    "timestamp": 1659321000
}
'''

def plant_recognition(request):
    if request.method == 'POST':
        # 接收前端数据
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data', {})
            base_str = image_data.get('base64')

        except json.JSONDecodeError:
            send_json = {  
                'code': 400, 
                'msg': 'json格式错误',  
                'data': {},   
            }
            return JsonResponse(data=send_json, status=400)


        pure_base_str = base_str.split(',')[1]

        # 调用千问接口进行植物识别
        send_json = {  
            'code': 200, 
            'msg': '植物识别成功',  
            'data': {}
        }
        return JsonResponse(data=send_json, status=200)






            


        
        
        

        

            
        