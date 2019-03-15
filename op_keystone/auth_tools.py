import re
from op_keystone.exceptions import CustomException
from utils import tools
from utils.dao import DAO


class AuthTools:
    """
    存放多种用于鉴权工具方法的类
    """

    _domain_model = DAO('partition.models.Domain')
    _user_model = DAO('identity.models.User')
    _group_model = DAO('identity.models.Group')
    _role_model = DAO('assignment.models.Role')
    _policy_model = DAO('assignment.models.Policy')
    _action_model = DAO('assignment.models.Action')

    _m2m_user_role_model = DAO('identity.models.M2MUserRole')
    _m2m_user_group_model = DAO('identity.models.M2MUserGroup')
    _m2m_group_role_model = DAO('identity.models.M2MGroupRole')
    _m2m_role_policy_model = DAO('assignment.models.M2MRolePolicy')

    def get_user_of_token(self, token_obj):
        """
        通过 token 对象获取对应 user 对象
        :param token_obj: token object
        :return: user object
        """
        # 获取 token 对象并检查是否过期
        now = tools.get_datetime_with_tz()
        expire_date = tools.get_datetime_with_tz(token_obj.expire_date)
        if now > expire_date:
            raise CustomException()

        # 获取 user 对象并返回
        user_obj = self._user_model.get_obj(uuid=token_obj.carrier)
        domain_obj = self._domain_model.get_obj(uuid=user_obj.domain)
        if not domain_obj.enable or not user_obj.enable:
            raise CustomException()

        # 根据 user 和 domain 是否为主，判定用户级别，并设置到请求对象中
        # 用户级别对权限的拒绝限制优先于策略， 级别对应：
        # 1 -> 全域    2 -> 跨域(除了主域)   3 -> 单个域
        if domain_obj.is_main:
            if user_obj.is_main:
                user_obj.level = 1
            else:
                user_obj.level = 2
        else:
            user_obj.level = 3

        return user_obj

    def get_policies_of_user(self, user_obj):
        """
        通过 user 对象获取包含对应 policy 对象的查询集
        :param user_obj: user object
        :return: query_set，query_set(policy_obj, ...)
        """
        # 用于存放 role 和 policy 的集合
        role_uuid_set = set([])
        policy_uuid_set = set([])

        # 将 user 对应的 role 的 uuid 放入集合
        role_uuid_list = self._m2m_user_role_model.get_field_list('role', user=user_obj.uuid)
        role_uuid_set |= set(role_uuid_list)

        # 将 user 对应的 group 所对应的 role 的 uuid 放入集合
        group_uuid_list = self._m2m_user_group_model.get_field_list('group', user=user_obj.uuid)
        for group_uuid in group_uuid_list:
            if not self._group_model.get_obj(uuid=group_uuid).enable:
                continue
            g_role_uuid_list = self._m2m_group_role_model.get_field_list('role', group=group_uuid)
            role_uuid_set |= set(g_role_uuid_list)

        # 分别集合中 role 对应的 policy 的 uuid 放入集合
        for role_uuid in role_uuid_set:
            if not self._role_model.get_obj(uuid=role_uuid).enable:
                continue
            policy_uuid_list = self._m2m_role_policy_model.get_field_list('policy', role=role_uuid)
            policy_uuid_set |= set(policy_uuid_list)

        # 所有 policy 列表并返回
        return self._policy_model.get_obj_qs(uuid__in=policy_uuid_set, enable=True)

    def judge_policies(self, policy_obj_qs, service_uuid, request_info):
        """
        判断请求是否匹配，若匹配返回 policy 的反馈字典
        :param policy_obj_qs: policy query set
        :param service_uuid: str, 服务 uuid
        :param request_info: tuple, 请求信息
        :return: tuple, access 标记和两个条件列表
        """
        allow_condition_list = []
        deny_condition_list = []

        access = False
        for policy_obj in policy_obj_qs:
            # 获取 policy 对象对应的 action 对象, 若 service 不符合，退出当次循环
            action_obj = self._action_model.get_obj(uuid=policy_obj.action)
            if action_obj.service != service_uuid:
                continue

            # 请求 view 不匹配期望 view，退出当次循环
            url = request_info['url']
            exp_url = action_obj.url
            if exp_url != '*' and not re.match(exp_url, url):
                continue

            # 请求 method 不匹配期望 method，退出当次循环
            method = request_info['method']
            exp_method = action_obj.method
            if exp_method != '*' and method != exp_method:
                continue

            # 请求 res 不匹配期望 res，退出当次循环
            res = request_info['routing_params'].get('uuid')
            exp_res_list = policy_obj.res.split(',')

            if policy_obj.effect == 'allow':
                if exp_res_list[0] == '*':
                    access = True
                    allow_condition_list.append(policy_obj.condition)
                elif res and res in exp_res_list:
                    access = True

            else:
                if exp_res_list[0] == '*':
                    if policy_obj.condition:
                        access = True
                        deny_condition_list.append(policy_obj.condition)
                    else:
                        access = False
                        break
                elif res:
                    if res in exp_res_list:
                        access = False
                        break
                else:
                    access = True
                    query_str = 'uuid=' + '|'.join(exp_res_list)
                    deny_condition_list.append(query_str)

        # 返回条件列表
        return access, allow_condition_list, deny_condition_list
