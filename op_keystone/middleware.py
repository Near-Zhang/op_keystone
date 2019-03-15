from django.utils.deprecation import MiddlewareMixin
from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils.dao import DAO
from django.conf import settings
from .auth_tools import AuthTools


class AuthMiddleware(MiddlewareMixin):
    """
    检查用户登陆状态的预请求中间件、校验用户权限的预路由中间件
    """

    _auth_tools = AuthTools()

    _domain_model = DAO('partition.models.Domain')
    _token_model = DAO('credence.models.Token')
    _service_model = DAO('catalog.models.Service')

    def process_request(self, request):

        # 免登录白名单路由处理
        request_route = (request.path, request.method.lower())
        if request_route in settings.ROUTE_WHITE_LIST:
            return

        # 登陆凭证校验
        try:
            # 获取登录凭证
            rq_token = request.META.get(settings.AUTH_HEADER)
            if not rq_token:
                raise CredenceInvalid(empty=True)

            try:
                # 获取 token 对象，若为 service token 则返回
                query_obj = self._token_model.parsing_query_str('type:0|2')
                token_obj = self._token_model.get_obj(query_obj, token=rq_token)
                if token_obj.type == 2:
                    request.service = self._service_model.get_obj(uuid=token_obj.carrier, enable=True)
                    return

                # 获取 user 对象，并设置到请求对象中
                request.user = self._auth_tools.get_user_of_token(token_obj)

            except CustomException:
                raise CredenceInvalid()

        except CredenceInvalid as e:
            return BaseView().exception_to_response(e)

    def process_view(self, request, callback, callback_args, callback_kwargs):

        # 无登录状态的请求，忽略鉴权
        if not getattr(request, 'user', None):
            return

        # 免鉴权白名单路由处理
        request_route = (request.path, request.method.lower())
        if request_route in settings.POLICY_WHITE_LIST:
            return

        # 开始鉴权
        try:
            user_obj = request.user
            # 用户级别为全域时，忽略鉴权
            if user_obj.level == 1:
                return

            # 整合服务和请求信息
            service_uuid = self._service_model.get_obj(name='keystone').uuid
            request_info = {
                'url': request.path,
                'method': request.method.lower(),
                'routing_params': callback_kwargs
            }

            # 获取 user 对象关联的 policy 列表，policy 判定处理后获取条件
            policy_obj_qs = self._auth_tools.get_policies_of_user(user_obj)
            access, allow_condition_list, deny_condition_list= self._auth_tools.judge_policies(
                policy_obj_qs, service_uuid, request_info)

            if not access:
                raise CustomException()

            request.condition_tuple = (allow_condition_list, deny_condition_list)

        except CustomException:
            return BaseView().exception_to_response(PermissionDenied())
