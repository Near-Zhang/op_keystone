from op_keystone.exceptions import CustomException, PermissionDenied
from op_keystone.base_view import M2MRelationView
from utils.dao import DAO
from utils import tools


class RoleToPolicyView(M2MRelationView):
    """
    通过角色，对将其关联的策略进行增、删、改、查
    """

    def __init__(self):
        from_model = 'assignment.models.Role'
        to_model = 'assignment.models.Policy'
        m2m_model = 'assignment.models.M2MRolePolicy'
        super().__init__(from_model, to_model, m2m_model)

    def post(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 域权限级别的请求，禁止修改其他 domain 的 role，跨域权限级别的请求，禁止修改主 domain 的 role
            if (request.privilege_level == 3 and role_obj.domain != request.user.domain) or \
                    (request.privilege_level == 2 and role_obj.domain == request.user.domain):
                raise PermissionDenied()

            # 提取参数
            policy_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            policy_opts_dict = self.extract_opts(request_params, policy_opts)

            # 获取需要添加的列表
            policy_uuid_set = set(policy_opts_dict['uuid_list'])
            old_policy_uuid_set = set(self.m2m_model.get_field_list('policy', role=role_uuid))
            add_policy_uuid_list = list(policy_uuid_set - old_policy_uuid_set)

            # 添加多对多关系, 如果 role 内置，policy 必须内置，狗则需要是内置的或者和 role 在同一 domain
            for policy_uuid in add_policy_uuid_list:
                try:
                    self.policy_model.get_obj(uuid=policy_uuid, builtin=True)
                except ObjectNotExist as e:
                    if role_obj.builtin:
                        raise e
                    self.policy_model.get_obj(uuid=policy_uuid, domain=role_obj.domain)
                self.m2m_model.create_obj(role=role_uuid, policy=policy_uuid)

            # 获取关联的 policy 列表
            policy_dict_list = self.get_policy_list(request, role_uuid)

            # 返回关联的 policy 列表
            data = tools.paging_list(policy_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 域权限级别的请求，禁止修改其他 domain 的 role，跨域权限级别的请求，禁止修改主 domain 的 role
            if (request.privilege_level == 3 and role_obj.domain != request.user.domain) or \
                    (request.privilege_level == 2 and role_obj.domain == request.user.domain):
                raise PermissionDenied()

            # 提取参数
            policy_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            policy_opts_dict = self.extract_opts(request_params, policy_opts)

            # 获取需要添加和删除的列表
            policy_uuid_set = set(policy_opts_dict['uuid_list'])
            old_policy_uuid_set = set(self.m2m_model.get_field_list('policy', role=role_uuid))
            add_policy_uuid_list = list(policy_uuid_set - old_policy_uuid_set)
            del_policy_uuid_list = list(old_policy_uuid_set - policy_uuid_set)

            # 添加多对多关系, 如果 role 内置，policy 必须内置，狗则需要是内置的或者和 role 在同一 domain
            for policy_uuid in add_policy_uuid_list:
                try:
                    self.policy_model.get_obj(uuid=policy_uuid, builtin=True)
                except ObjectNotExist as e:
                    if role_obj.builtin:
                        raise e
                    self.policy_model.get_obj(uuid=policy_uuid, domain=role_obj.domain)
                self.m2m_model.create_obj(role=role_uuid, policy=policy_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(role=role_uuid, policy__in=del_policy_uuid_list).delete()

            # 获取关联的 policy 列表
            policy_dict_list = self.get_policy_list(request, role_uuid)

            # 返回关联的 policy 列表
            data = tools.paging_list(policy_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 域权限级别的请求，禁止修改其他 domain 的 role，跨域权限级别的请求，禁止修改主 domain 的 role
            if (request.privilege_level == 3 and role_obj.domain != request.user.domain) or \
                    (request.privilege_level == 2 and role_obj.domain == request.user.domain):
                raise PermissionDenied()

            # 提取参数
            policy_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            policy_opts_dict = self.extract_opts(request_params, policy_opts)

            # 获取需要添加和删除的列表
            policy_uuid_set = set(policy_opts_dict['uuid_list'])
            old_policy_uuid_set = set(self.m2m_model.get_field_list('policy', role=role_uuid))
            del_policy_uuid_list = list(old_policy_uuid_set & policy_uuid_set)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(role=role_uuid, policy__in=del_policy_uuid_list).delete()

            # 获取关联的 policy 列表
            policy_dict_list = self.get_policy_list(request, role_uuid)

            # 返回关联的 policy 列表
            data = tools.paging_list(policy_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def get_policy_list(self, request, role_uuid):
        """
        获取最新 policy 列表
        :param request: object, 请求对象
        :param role_uuid: str, 角色 uuid
        :return: list
        """
        policy_uuid_list = self.m2m_model.get_field_list('policy', role=role_uuid)

        # 非跨域权限只能获取内置和本域的 policy
        if request.privilege_level == 3:
            policy_dict_list = []
            custom_policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list,
                                                                      domain=request.user.domain)
            builtin_policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list,
                                                                       builtin=True)
            policy_dict_list.extend(custom_policy_dict_list)
            policy_dict_list.extend(builtin_policy_dict_list)
        else:
            policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list)

        return policy_dict_list


class PolicyToRoleView(M2MRelationView):
    """
    通过策略，对将其关联的角色进行增、删、改、查
    """

    def __init__(self):
        from_model = 'assignment.models.Policy'
        to_model = 'assignment.models.Role'
        m2m_model = 'assignment.models.M2MRolePolicy'
        super().__init__(from_model, to_model, m2m_model)

    def post(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 除了内置策略，域权限级别的请求，禁止修改其他 domain 的 policy，跨域权限级别的请求，禁止修改主 domain 的 policy
            if not policy_obj.builtin:
                if (request.privilege_level == 3 and policy_obj.domain != request.user.domain) or \
                        (request.privilege_level == 2 and policy_obj.domain == request.user.domain):
                    raise PermissionDenied()

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 获取需要添加的列表
            role_uuid_set = set(role_opts_dict['uuid_list'])
            old_role_uuid_set = set(self.m2m_model.get_field_list('role', policy=policy_uuid))
            add_role_uuid_list = list(role_uuid_set - old_role_uuid_set)

            # 添加多对多关系, 如果 policy 内置，对于域权限级别的请求，role 必须和登录用户同一 domain，
            # 对于跨域权限级别的请求，不允许添加主 domain 的 role；否则 role 必须和 policy 同一 domain
            for role_uuid in add_role_uuid_list:
                if policy_obj.builtin:
                    role_obj = self.role_model.get_obj(uuid=role_uuid)
                    if (request.privilege_level == 2 and role_obj.domain == request.user.domain) or \
                            (request.privilege_level == 3 and role_obj.domain != request.user.domain):
                        raise PermissionDenied()
                else:
                    self.role_model.get_obj(uuid=role_uuid, domain=policy_obj.domain)
                self.m2m_model.create_obj(policy=policy_uuid, role=role_uuid)

            # 获取最新 role 列表
            role_dict_list = self.get_role_list(request, policy_uuid)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 除了内置策略，域权限级别的请求，禁止修改其他 domain 的 policy，跨域权限级别的请求，禁止修改主 domain 的 policy
            if not policy_obj.builtin:
                if (request.privilege_level == 3 and policy_obj.domain != request.user.domain) or \
                        (request.privilege_level == 2 and policy_obj.domain == request.user.domain):
                    raise PermissionDenied()

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 获取需要添加和删除的列表
            role_uuid_set = set(role_opts_dict['uuid_list'])
            old_role_uuid_set = set(self.m2m_model.get_field_list('role', policy=policy_uuid))
            add_role_uuid_list = list(role_uuid_set - old_role_uuid_set)
            del_role_uuid_list = list(old_role_uuid_set - role_uuid_set)

            # 添加多对多关系, 如果 policy 内置，对于域权限级别的请求，role 必须和登录用户同一 domain，
            # 对于跨域权限级别的请求，不允许添加主 domain 的 role；否则 role 必须和 policy 同一 domain
            for role_uuid in add_role_uuid_list:
                if policy_obj.builtin:
                    role_obj = self.role_model.get_obj(uuid=role_uuid)
                    if (request.privilege_level == 2 and role_obj.domain == request.user.domain) or \
                            (request.privilege_level == 3 and role_obj.domain != request.user.domain):
                        raise PermissionDenied()
                else:
                    self.role_model.get_obj(uuid=role_uuid, domain=policy_obj.domain)
                self.m2m_model.create_obj(policy=policy_uuid, role=role_uuid)

            # 删除多对多关系，对于内置 policy，不允许跨域权限级别的请求删除主 domain 的 role，
            # 只允许域权限级别的请求删除与登录用户所在 domain 的 role
            for role_uuid in del_role_uuid_list:
                m2m_obj = self.m2m_model.get_obj(policy=policy_uuid, role=role_uuid)
                try:
                    role_obj = self.role_model.get_obj(uuid=role_uuid)
                except ObjectNotExist:
                    self.m2m_model.delete_obj(m2m_obj)
                else:
                    if policy_obj.builtin:
                        if (request.privilege_level == 2 and role_obj.domain == request.user.domain) or \
                                (request.privilege_level == 3 and role_obj.domain != request.user.domain):
                            raise PermissionDenied()
                    self.m2m_model.delete_obj(m2m_obj)

            # 获取最新 role 列表
            role_dict_list = self.get_role_list(request, policy_uuid)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 除了内置策略，域权限级别的请求，禁止修改其他 domain 的 policy，跨域权限级别的请求，禁止修改主 domain 的 policy
            if not policy_obj.builtin:
                if (request.privilege_level == 3 and policy_obj.domain != request.user.domain) or \
                        (request.privilege_level == 2 and policy_obj.domain == request.user.domain):
                    raise PermissionDenied()

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 获取需要添加和删除的列表
            role_uuid_set = set(role_opts_dict['uuid_list'])
            old_role_uuid_set = set(self.m2m_model.get_field_list('role', policy=policy_uuid))
            del_role_uuid_list = list(old_role_uuid_set & role_uuid_set)

            # 删除多对多关系，对于内置 policy，不允许跨域权限级别的请求删除主 domain 的 role，
            # 只允许域权限级别的请求删除与登录用户所在 domain 的 role
            for role_uuid in del_role_uuid_list:
                m2m_obj = self.m2m_model.get_obj(policy=policy_uuid, role=role_uuid)
                try:
                    role_obj = self.role_model.get_obj(uuid=role_uuid)
                except ObjectNotExist:
                    self.m2m_model.delete_obj(m2m_obj)
                else:
                    if policy_obj.builtin:
                        if (request.privilege_level == 2 and role_obj.domain == request.user.domain) or \
                                (request.privilege_level == 3 and role_obj.domain != request.user.domain):
                            raise PermissionDenied()
                    self.m2m_model.delete_obj(m2m_obj)

            # 获取最新 role 列表
            role_dict_list = self.get_role_list(request, policy_uuid)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def get_role_list(self, request, policy_uuid):
        """
        获取最新 policy 列表
        :param request: object, 请求对象
        :param policy_uuid: str, 策略 uuid
        :return: list
        """
        role_uuid_list = self.m2m_model.get_field_list('role', policy=policy_uuid)

        # 非跨域权限只能获取内置和本域的 role
        if request.privilege_level == 3:
            role_dict_list = []
            custom_role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list,
                                                                  domain=request.user.domain)
            builtin_role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list,
                                                                   builtin=True)
            role_dict_list.extend(custom_role_dict_list)
            role_dict_list.extend(builtin_role_dict_list)
        else:
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

        return role_dict_list

