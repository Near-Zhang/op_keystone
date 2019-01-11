from django.utils.deprecation import MiddlewareMixin
from op_keystone.exceptions import *
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
    def error_json_respond(exception):
        res = {
            'code': exception.code,
            'data': None,
            'message': exception.__message__()
        }
        return JsonResponse(res)

    @staticmethod
    def check_token_valid(token):
        now = get_datetime_with_tz()
        expire_date = get_datetime_with_tz(token.expire_date)
        if now > expire_date:
            raise CredenceInvalid()

    def process_request(self, request):

        # 白名单路由处理
        if request.path in self.path_white_list:
            return

        # 登陆凭证检查
        try:
            rq_uuid = request.COOKIES.get('uuid')
            rq_token = request.COOKIES.get('token')
            if not rq_uuid or not rq_token:
                raise CredenceInvalid(empty=True)

            token = self.token_model.get_object(user=rq_uuid, token=rq_token)
            self.check_token_valid(token)
            user = self.user_model.get_object(uuid=rq_uuid)
            if not user.enable:
                raise CustomException()
            request.user = user
            return

        except CustomException as e:
            return self.error_json_respond(e)
