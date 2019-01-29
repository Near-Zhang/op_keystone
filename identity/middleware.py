from django.utils.deprecation import MiddlewareMixin
from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils.tools import get_datetime_with_tz
from utils.dao import DAO
from django.http.response import JsonResponse


class AuthMiddleware(MiddlewareMixin):
    """
    仅仅检查用户登陆的中间件
    """

    domain_model = DAO('partition.models.Domain')
    user_model = DAO('identity.models.User')
    token_model = DAO('credence.models.Token')

    route_white_list = [
        ('/identity/login/', 'post')
    ]

    def process_request(self, request):

        # 白名单路由处理
        request_route = (request.path, request.method.lower())
        if request_route in self.route_white_list:
            return

        # 登陆凭证校验
        try:
            # 获取登录凭证
            rq_uuid = request.COOKIES.get('uuid')
            rq_token = request.COOKIES.get('token')
            if not rq_uuid or not rq_token:
                raise CredenceInvalid(empty=True)

            try:
                # 检查凭证是否过期
                token = self.token_model.get_obj(user=rq_uuid, token=rq_token)
                now = get_datetime_with_tz()
                expire_date = get_datetime_with_tz(token.expire_date)
                if now > expire_date:
                    raise CustomException()

                # 获取用户信息并将其附在请求上
                user = self.user_model.get_obj(uuid=rq_uuid)
                domain = self.domain_model.get_obj(uuid=user.domain)
                if not domain.enable or not user.enable:
                    raise CustomException()
                request.user = user
                return

            except CustomException:
                raise CredenceInvalid()

        except CredenceInvalid as e:
            return BaseView().exception_to_response(e)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        print(callback.view_class)
        print(callback.view_class.__name__)
        print(callback.view_class.__module__ + '.' + callback.view_class.__name__)
        print(callback_kwargs)
