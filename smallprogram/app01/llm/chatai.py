from app01.models import ChatSessionMessage
import uuid
import json


# 千问的ai接口
class OpenaiQianwenapi:
    def __init__(self, request):
        self.request = request
    












# 有关历史记录的获取
# class ChatAiInformation:
#     def __init__(self, request):
#         self.request = request

#     # 获取session_id
#     def acquire_session_id(self):
#         data = json.loads(self.request.body)
#         session_id = data.get('session_id')
#         if not session_id:
#             session_id = uuid.uuid4().hex
#         return session_id
    
#     def acquire_history_message(self, session_id):
#         history_message = []

#         data_exist = ChatSessionMessage.objects.filter(session_id=session_id).exists()
#         if not data_exist:
#             return history_message
        
#         row_obj_history = ChatSessionMessage.objects.filter(session_id=session_id).order_by('create_time')



        

    