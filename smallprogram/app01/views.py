import json
import base64
import threading
import uuid
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
from app01.models import UserImageInfo
from app01.models import UserAiImage
from app01.models import HistoryAiMessage
from app01.pthread import ai_pthread
from app01.models import InstructionManual
from app01.llm.chatai import LangChainChat
from app01.llm.appendaimessage import create_json_history
from app01.models import HistoryAiMessage



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
                'data': None,   
            }
            return JsonResponse(data=send_json, status=400)


        # 表单信息查验
        model = formdetection.UserLoginModelForm(data=data)
        if not model.is_valid():
            error_dirt = {field: error[0] for field, error in model.errors.items()}
            send_json = {  
                'code': 422, 
                'msg': '提交到数据错误',
                'data': error_dirt,
            }
            return JsonResponse(data=send_json, status=422)
        
        # 用户信息查询  
        user_info = UserInfo.objects.filter(phone=phone).first()
        if not user_info:
            send_json = {  
                'code': 404, 
                'msg': '用户不存在',  
                'data': None,   
            }
            return JsonResponse(data=send_json, status=404)

        # 密码加密验证
        if encrypt.encrypt_password(password) == user_info.password:
            jwt_token = tokenjwt.generate_token(user_info.id)

            print(jwt_token)

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
                'data': None,    
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
                'data': None,   
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
                'data': None,   
            }
            return JsonResponse(data=send_json, status=429)
        
        # 生成验证码
        sms = utilityfunc.random_string()
        print('111111111111111111', sms, '111111111111111111')
        cache.set(f'sms_code_{phone}', sms, timeout=300)


        # 发送验证码
        sendsms.send_sms(phone, sms)

        cache.set(f'sms_cooldown_{phone}', True, timeout=60)


        send_json = {  
            'code': 200, 
            'msg': '验证码发送成功',  
            'data': None,   
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
                'data': None,   
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
        

        obj_new = modelform.save()
        
        UserImageInfo.objects.create(user=obj_new)

        send_json = {  
            'code': 200, 
            'msg': '注册成功',  
            'data': None,   
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
                'data': None,   
            }
            return JsonResponse(data=send_json, status=401)

    
        Blacklist.objects.create(token=request.token)
        

        UserInfo.objects.filter(id=user_id).delete()
        send_json = {  
            'code': 200, 
            'msg': '用户已删除',  
            'data': None,   
            }
        
        return JsonResponse(data=send_json, status=200)


def logout(request):
    if request.method == 'GET':
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
                'data': None,   
            }
            return JsonResponse(data=send_json, status=404)



        # 验证码发送频率限制
        if cache.get(f'sms_cooldown_change_password_{user_phone}'):
            send_json = {  
                'code': 429, 
                'msg': '发送频率过快',  
                'data': None,   
            }
            return JsonResponse(data=send_json, status=429)
        

        sms = utilityfunc.random_string()
        cache.set(f'sms_code_change_password_{user_phone}', sms, timeout=300)

        sendsms.send_sms(user_phone, sms)

        cache.set(f'sms_cooldown_change_password_{user_phone}', True, timeout=60)

        send_json = {  
            'code': 200, 
            'msg': '验证码发送成功',  
            'data': None,   
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
                'data': None,   
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
            'data': None,
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
                'data': None,   
            }
            return JsonResponse(data=send_json, status=400)


        pure_base_str = base_str.split(',')[1]

        # 调用千问接口进行植物识别
        send_json = {  
            'code': 200, 
            'msg': '植物识别成功',  
            'data': None
        }
        return JsonResponse(data=send_json, status=200)



def user_home(request) :
    if request.method == 'GET':
        # 接收前端数据
        user_id = request.user_id  # 这里需要从token中获取用户id
        
        # 获取用户信息
        user_info = UserInfo.objects.filter(id=user_id).first()

        user_image_info = UserImageInfo.objects.filter(user=user_info).first()

        if user_image_info.image_data == None:
            data_json = {
                'code': 200,
                'msg': '用户信息获取成功',
                'data': {
                    'user_name': user_info.username,
                    'user_image': None,
                    }
                }
            return JsonResponse(data=data_json, status=200)
            
        if user_image_info.image_data != None:
            data_json = {
                'code': 200,
                'msg': '用户信息获取成功',
                'data': {
                    'user_name': user_info.username,
                    'user_image': f"data:image/png;base64,{base64.b64encode(user_image_info.image_data).decode('utf-8')}",
                    }
                }
            return JsonResponse(data=data_json, status=200)
        

def edit_profile_image(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        user_image = data.get('user_image')
        user_id = request.user_id  # 这里需要从token中获取用户id

        # 获取用户信息
        user_info = UserInfo.objects.filter(id=user_id).first()

        if 'base64,' in user_image:
            user_image = user_image.split(',')[1]

        user_image_bytes = base64.b64decode(user_image)  

        # 保存用户头像图片
        UserImageInfo.objects.filter(user=user_info).update(image_data=user_image_bytes)

        data_json = {
            'code': 200,
            'msg': '用户头像修改成功',
            'data': None,
            }
        return JsonResponse(data=data_json, status=200)
            

def edit_nickname(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        user_nickname = data.get('user_nickname')
        
        user_id = request.user_id  # 这里需要从token中获取用户id

        if len(user_nickname) < 5 or len(user_nickname) > 10:
            data_json = {
                'code': 400,
                'msg': '昵称长度必须在5-10个字符之间',
                'data': None,
                }
            return JsonResponse(data=data_json, status=400)
        
        # 获取用户信息
        UserInfo.objects.filter(id=user_id).update(username=user_nickname)

        data_json = {
            'code': 200,
            'msg': '用户昵称修改成功',
            'data': None,
            }
        return JsonResponse(data=data_json, status=200)



def user_change_page(request):
    if request.method == 'GET':
        # 接收前端数据
        user_id = request.user_id  # 这里需要从token中获取用户id

        # 获取用户信息
        user_info = UserInfo.objects.filter(id=user_id).first()

        data_json = {
            'code': 200,
            'msg': '用户信息获取成功',
            'data': {
                'phone': user_info.phone,
            }
        }
        return JsonResponse(data=data_json, status=200)






def login_change_password_send_sms(request):
    if request.method == 'GET':
        # 接收前端数据
        user_id = request.user_id  # 这里需要从token中获取用户id

        row_obj = UserInfo.objects.filter(id=user_id).first()
        user_phone = row_obj.phone

        # 验证码发送频率限制

        if cache.get(f'sms_cooldown_login_change_password_{user_phone}'):
            send_json = {  
                'code': 429, 
                'msg': '发送频率过快',  
                'data': None,   
            }
            return JsonResponse(data=send_json, status=429)

        
        sms = utilityfunc.random_string()
        print('111111111111111111', sms, '111111111111111111')

        cache.set(f'sms_code_login_change_password_{user_phone}', sms, timeout=300)

        sendsms.send_sms(user_phone, sms)

        cache.set(f'sms_cooldown_login_change_password_{user_phone}', True, timeout=60)

        send_json = {  
            'code': 200, 
            'msg': '验证码发送成功',  
            'data': None,   
            }
        return JsonResponse(data=send_json, status=200)



def login_change_password(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        
        user_id = request.user_id  # 这里需要从token中获取用户id

        row_obj = UserInfo.objects.filter(id=user_id).first()

        data['phone'] = row_obj.phone


        # 表单信息查验
        modelform = formdetection.UserLoginChangePasswordModelForm(data=data, instance=row_obj)
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

        # token拉入黑名单
        Blacklist.objects.create(token=request.token)

        data_json = {
            'code': 200,
            'msg': '修改密码成功',
            'data': None,
            }
            
        return JsonResponse(data=data_json, status=200)



def core_function_get_picture(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        user_id = request.user_id  # 这里需要从token中获取用户id
        user_image = data.get('user_image')


        if 'base64,' in user_image:
            user_image = user_image.split(',')[1]

        user_image_bytes = base64.b64decode(user_image) 
    
        # 保存检测图片
        uuid_new = uuid.uuid4()

        user_key = UserInfo.objects.filter(id=user_id).first()

        
        UserAiImage.objects.create(user=user_key, image_data=user_image_bytes, uuid=uuid_new)

        # 开辟线程处理这个

        pthread = threading.Thread(target=ai_pthread.ai_pthread_get_image_info, args=(uuid_new, ))
        pthread.start()

        json_data = {
            'code': 200,
            'msg': '图片上传成功',
            'data': {
                'uuid': str(uuid_new),
                }
            }
        return JsonResponse(data=json_data, status=200)


def request_info_exist(request):
    if request.method == 'POST':

        # 接收前端数据
        data = json.loads(request.body)
        uuid = data.get('uuid')
        user_id = request.user_id  # 这里需要从token中获取用户id

        # 数据库查询
        row_obj = UserAiImage.objects.filter(uuid=uuid).first()

        if row_obj.image_info == None:
            json_data = {
                'code': 404,
                'msg': '图片检测暂未结束',
                'data': None,
            }
            return JsonResponse(data=json_data, status=200)
        
        # 可能添加数据库的信息处理
        picture_info = InstructionManual.objects.filter(title=row_obj.image_info).first()

        history = []

        history.append(
            {
                "role": "system",
                "type": "text",
                "content": picture_info.content,
            }
        )
        
        row_obj = UserInfo.objects.filter(id=user_id).first()


        HistoryAiMessage.objects.create(uuid=uuid, user=row_obj, message=history)


        json_data = {
            'code': 200,
            'msg': '图片检测完成',
            'data': {
                'picture_info': picture_info.content,
            },
        }
        return JsonResponse(data=json_data, status=200)


def core_function_get_history_picture(request):
    if request.method == 'GET':
        # 接收前端数据
        user_id = request.user_id  # 这里需要从token中获取用户id

        # 数据库查询
        user_info_obj = UserInfo.objects.filter(id=user_id).first()

        user_judge_exist = UserAiImage.objects.filter(user=user_info_obj).exists()


        if not user_judge_exist:
            json_data = {
                'code': 404,
                'msg': '暂无历史图片',
                'data': {
                    'history': None,
                }
            }
            return JsonResponse(data=json_data, status=200)

        user_ai_image_obj = UserAiImage.objects.filter(user=user_info_obj).order_by('-add_time')[:10]

        history = []

        for obj in user_ai_image_obj:
            image_info = {
                'picture':f'data:image/png;base64,{base64.b64encode(obj.image_data).decode("utf-8")}',
                'picture_uuid':str(obj.uuid),
                'picture_time':obj.add_time.strftime('%Y-%m-%d'),
                'picture_info':obj.image_info,
            }
            
            history.append(image_info)

        json_data = {
            'code': 200,
            'msg': '历史图片获取成功',
            'data': {
                'history':history,
            }
        }
        return JsonResponse(data=json_data, status=200)



def core_function_get_history_message(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        uuid = data.get('uuid')

        # 数据库查询
        row_obj = HistoryAiMessage.objects.filter(uuid=uuid).first()

        if row_obj == None:
            json_data = {
                'code': 404,
                'msg': '暂无历史消息',
                'data': {}
            }

        image_obj = UserAiImage.objects.filter(uuid=uuid).first()


        json_data = {
            'code': 200,
            'msg': '历史消息获取成功',
            'data': {
                'history_picture':f"data:image/png;base64,{base64.b64encode(image_obj.image_data).decode('utf-8')}",
                'history_message':row_obj.message,
                }
            }
            
        return JsonResponse(data=json_data, status=200)

         
def core_function_multi_conversaion(request):
    if request.method == 'POST':
        # 接收前端数据
        data = json.loads(request.body)
        user_id = request.user_id  # 这里需要从token中获取用户id
        uuid = data.get('uuid')
        message = data.get('message')
        chat = LangChainChat(uuid)

        row_obj =  HistoryAiMessage.objects.filter(uuid=uuid).first()
        history_message = row_obj.message


        chat_history = {
            'conversation': history_message,
        }

        chat.load_conversation_history(uuid, chat_history)

        response = chat.run_chat(input_text=message, language="中文", is_streaming=True)

        history_message.append(
            {
                "role": "user",
                "type": "text",
                "content": message,
            },
        )

        history_message.append(
            {
            "role": "system",
            "type": "text",
            "content": response,
            }
        )

        HistoryAiMessage.objects.filter(uuid=uuid).update(message=history_message)       
        
        json_data = {
            'code': 200,
            'msg': '多轮对话成功',
            'data': {
                'ai_response':response,
            }
        }

        return JsonResponse(data=json_data, status=200)







