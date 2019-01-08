from django.utils.deprecation import MiddlewareMixin
from utils.tools import get_datetime_with_tz
from utils import dao
from django.http.response import JsonResponse


class AuthMiddleware(MiddlewareMixin):

    path_white_list = [
        '/identity/login/'
    ]

    @staticmethod
    def set_user_for_request(request, uuid):
        user = dao.get_object_from_model('identity.models.User', uuid=uuid)
        if user and user.enable:
            request.user = user
            return True

    @staticmethod
    def error_json_respond(message):
        res = {
            'code': 403,
            'data': None,
            'message': message
        }
        return JsonResponse(res)

    @staticmethod
    def check_token_valid(token):
        if token:
            now = get_datetime_with_tz()
            expire_date = get_datetime_with_tz(token.expire_date)
            if now <= expire_date:
                return True

    def process_request(self, request):
        # 白名单路由处理
        if request.path in self.path_white_list:
            return
        # 登陆凭证检查
        rq_uuid = request.COOKIES.get('uuid')
        rq_token = request.COOKIES.get('token')
        if rq_uuid and rq_token:
            token = dao.get_object_from_model('credence.models.Token', user=rq_uuid, token=rq_token)
            if self.check_token_valid(token):
                if not self.set_user_for_request(request, rq_uuid):
                    return self.error_json_respond('UserInvalid:the user is non-existent or invalid' )
            else:
                return self.error_json_respond('TokenInvalid:the token is invalid')
        else:
            return self.error_json_respond('CredenceMissed:access credence is required')


