from app01.llm import chatai
from app01.models import UserAiImage
from base64 import b64encode
import uuid

def ai_pthread_get_image_info(uuid):
    # 加载大模型对应的类
    chatai_obj = chatai.QwenVL72bClient()
    # 获取图片信息
    image_info = UserAiImage.objects.filter(uuid=uuid).first().image_data


    # 将图片信息编码为base64格式字符串
    image_info_base64_str = b64encode(image_info).decode('utf-8')

    # 向模型发送请求,并且获取信息
    image_tool_name = chatai_obj.send_request_with_base64_image(image_info_base64_str)

    # 将信息保存到数据库中
    UserAiImage.objects.filter(uuid=uuid).update(image_info=image_tool_name)
    



    
    
