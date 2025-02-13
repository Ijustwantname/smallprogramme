from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from app01.tools import tokenjwt
from app01.models import UserInfo


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # 判断是否需要中间件拦截
        if request.path in ['/api/login/', '/api/register/', '/api/register/send_sms/']:
            return None
        
        
        # 自定义中间件逻辑
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            data_json = {
                'code': 401,
                'msg': '未提供 Token'
            }

            return JsonResponse(data_json, status=401)

        token = auth_header.split(' ')[1]

        # 验证 token
        payload = tokenjwt.verify_jwt(token)
        if not payload:
            data_json = {
                'code': 401,
                'msg': 'Token 无效或已过期'
            }
            return JsonResponse(data_json, status=401)
        
        # 检验用户是否存在
        exist = UserInfo.objects.filter(id=payload.get('user_id')).exists()
        if not exist:
            data_json = {
                'code': 401,
                'msg': '用户不存在'
                }
            return JsonResponse(data_json, status=401)
        

        request.user_id = payload.get('user_id')
        return None





