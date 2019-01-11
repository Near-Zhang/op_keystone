from django.utils.deprecation import MiddlewareMixin
from op_keystone.exceptions import CustomException
from utils.tools import get_datetime_with_tz
from utils.dao import DAO
from django.http.response import JsonResponse


class AuthMiddleware(MiddlewareMixin):
    """
    仅仅检查用户登陆的中间件
    """

    user_model = DAO('identity.models.User')
    token_model = DAO('credence.models.Token')

    path_white_list = [
        '/identity/login/'
    ]

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
            try:
                token = self.token_model.get_object(user=rq_uuid, token=rq_token)
                if self.check_token_valid(token):
                    user = self.user_model.get_object(uuid=rq_uuid)
                    if user.enable:
                        request.user = user

            except CustomException as e:
                return self.error_json_respond('CredenceInvalid: the user or token is invalid')
        else:
            return self.error_json_respond('CredenceMissed: access credence is required')
