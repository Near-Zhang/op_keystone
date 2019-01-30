from django.utils.deprecation import MiddlewareMixin
from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO


class AuthMiddleware(MiddlewareMixin):
    """
    检查用户登陆状态的中间件、校验用户权限的中间件
    """

    domain_model = DAO('partition.models.Domain')
    user_model = DAO('identity.models.User')
    token_model = DAO('credence.models.Token')
    policy_model = DAO('assignment.models.Policy')

    m2m_user_role_model = DAO('identity.models.M2MUserRole')
    m2m_user_group_model = DAO('identity.models.M2MUserGroup')
    m2m_group_role_model = DAO('identity.models.M2MGroupRole')
    m2m_role_policy_model = DAO('assignment.models.M2MRolePolicy')

    route_white_list = [
        ('/identity/login/', 'post')
    ]

    policy_white_list = [

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
                now = tools.get_datetime_with_tz()
                expire_date = tools.get_datetime_with_tz(token.expire_date)
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

        # 忽略无需登录的请求
        if not getattr(request, 'user', None):
            return

        # 开始鉴权
        try:
            view = callback.view_class.__module__ + '.' + callback.view_class.__name__
            method = request.method.lower()
            view_params_dict = callback_kwargs
            request_params_dict = BaseView().get_params_dict(request, nullable=True)

            action_info = (view, method, view_params_dict, request_params_dict)

            try:
                role_uuid_set = set([])
                policy_uuid_set = set([])

                # 将用户对应的 role uuid 放入集合
                user_uuid = request.user.uuid
                u_role_uuid_list = self.m2m_user_role_model.get_field_list('role', user=user_uuid)
                role_uuid_set = role_uuid_set | set(u_role_uuid_list)

                # 将用户所在用户组对应的 role uuid 放入集合
                group_uuid_list = self.m2m_user_group_model.get_field_list('group', user=user_uuid)
                for group_uuid in group_uuid_list:
                    g_role_uuid_list = self.m2m_group_role_model.get_field_list('role', group=group_uuid)
                    role_uuid_set = role_uuid_set | set(g_role_uuid_list)

                # 获取所有 role 对应的 policy uuid 放入集合
                for role_uuid in role_uuid_set:
                    policy_uuid_list = self.m2m_role_policy_model.get_field_list('policy', role=role_uuid)
                    policy_uuid_set = role_uuid_set | set(policy_uuid_list)

                # 获取所有的 policy 列表
                policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_set)

                # 对策略进行逐条判断，默认策略是拒绝访问
                access = False
                for policy_dict in policy_dict_list:
                    effect = self.judge_policy(action_info, policy_dict)
                    if effect == 'allow':
                        access = True
                    elif effect == 'deny':
                        access = False
                        break

                if not access:
                    raise CustomException()

            except CustomException:
                raise PermissionDenied()

        except PermissionDenied as e:
            return BaseView().exception_to_response(e)

    @staticmethod
    def judge_policy(action_info, policy):
        """
        判断请求是否匹配策略，若匹配返回策略的效力
        :param action_info: tuple, 请求动作信息
        :param policy: dict, 策略对象序列化的字典
        :return: None|str
        """
        if policy.get('view') != '*' and policy.get('view') != action_info[0]:
            return

        if policy.get('method') != '*' and policy.get('method') != action_info[1]:
            return

        view_params = policy.get('view_params')
        view_params_match = False
        for p in view_params:
            match = True
            for k in action_info[2]:
                for k in action_info[2]:
                    if p.get(k) and p.get(k) != action_info[2].get(k):
                        match = False
            if match:
                view_params_match = True
                break
        if not view_params_match:
            return

        request_params = policy.get('request_params')
        request_params_match = False
        for p in request_params:
            match = True
            for k in action_info[3]:
                if p.get(k) and p.get(k) != action_info[3].get(k):
                    match = False
            if match:
                request_params_match = True
                break
        if not request_params_match:
            return

        return policy.get('effect')

