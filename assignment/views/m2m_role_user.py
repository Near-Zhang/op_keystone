from op_keystone.exceptions import CustomException, PermissionDenied
from op_keystone.base_view import M2MRelationView
from utils import tools
from utils.dao import DAO


class RoleToUserView(M2MRelationView):
    """
    通过角色，对将其关联的用户进行增、删、改、查
    """

    def __init__(self):
        from_model = 'assignment.models.Role'
        to_model = 'identity.models.User'
        m2m_model = 'identity.models.M2MUserRole'
        super().__init__(from_model, to_model, m2m_model)

    def post(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 除了内置 role，域权限级别的请求，禁止修改其他 domain 的 role，跨域权限级别的请求，禁止修改主 domain 的 role
            if not role_obj.builtin:
                if (request.privilege_level == 3 and role_obj.domain != request.user.domain) or \
                        (request.privilege_level == 2 and role_obj.domain == request.user.domain):
                    raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加的 uuid 列表
            user_uuid_set = set(user_opts_dict['uuid_list'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', role=role_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)

            # 添加多对多关系，如果 role 是内置，保证 user 存在，跨域权限级别的请求不允许添加主 domain 的 user，
            # 域权限级别的请求只允许添加与登录用户所在 domain 的 user；role 不是内置，保证和 role 相同 domain 的 user 存在
            for user_uuid in add_user_uuid_list:
                if role_obj.builtin:
                    user_obj = self.user_model.get_obj(uuid=user_uuid)
                    if (request.privilege_level == 2 and user_obj.domain == request.user.domain) or \
                            (request.privilege_level == 3 and user_obj.domain != request.user.domain):
                        raise PermissionDenied()
                else:
                    self.user_model.get_obj(uuid=user_uuid, domain=role_obj.domain)
                self.m2m_model.create_obj(role=role_uuid, user=user_uuid)

            # 获取关联的 user 列表，对于内置 role，域权限级别的请求，只允许获取登录用户所在 domain 的 user
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            domain_opts = {'domain': request.user.domain} if role_obj.builtin and request.privilege_level == 3 else {}
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list, **domain_opts)

            # 返回关联的 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 除了内置 role，域权限级别的请求，禁止修改其他 domain 的 role，跨域权限级别的请求，禁止修改主 domain 的 role
            if not role_obj.builtin:
                if (request.privilege_level == 3 and role_obj.domain != request.user.domain) or \
                        (request.privilege_level == 2 and role_obj.domain == request.user.domain):
                    raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加和删除的列表
            user_uuid_set = set(user_opts_dict['uuid_list'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', role=role_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)
            del_user_uuid_list = list(old_user_uuid_set - user_uuid_set)

            # 添加多对多关系，如果 role 是内置，保证 user 存在，跨域权限级别的请求不允许添加主 domain 的 user，
            # 域权限级别的请求只允许添加与登录用户所在 domain 的 user；role 不是内置，保证和 role 相同 domain 的 user 存在
            for user_uuid in add_user_uuid_list:
                if role_obj.builtin:
                    user_obj = self.user_model.get_obj(uuid=user_uuid)
                    if (request.privilege_level == 2 and user_obj.domain == request.user.domain) or \
                            (request.privilege_level == 3 and user_obj.domain != request.user.domain):
                        raise PermissionDenied()
                else:
                    self.user_model.get_obj(uuid=user_uuid, domain=role_obj.domain)
                self.m2m_model.create_obj(role=role_uuid, user=user_uuid)

            # 删除多对多关系，对于 role 是内置的，不允许跨域权限级别的请求删除主 domain 的 user，
            # 只允许域权限级别的请求删除与登录用户所在 domain 的 user
            for user_uuid in del_user_uuid_list:
                m2m_obj = self.m2m_model.get_obj(role=role_uuid, user=user_uuid)
                try:
                    user_obj = self.user_model.get_obj(uuid=user_uuid)
                except ObjectNotExist:
                    self.m2m_model.delete_obj(m2m_obj)
                else:
                    if role_obj.builtin:
                        if (request.privilege_level == 2 and user_obj.domain == request.user.domain) or \
                                (request.privilege_level == 3 and user_obj.domain != request.user.domain):
                            raise PermissionDenied()
                    self.m2m_model.delete_obj(m2m_obj)

            # 获取关联的 user 列表，对于内置 role，域权限级别的请求，只允许获取登录用户所在 domain 的 user
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            domain_opts = {
                'domain': request.user.domain} if role_obj.builtin and request.privilege_level == 3 else {}
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list, **domain_opts)

            # 返回关联的 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 除了内置 role，域权限级别的请求，禁止修改其他 domain 的 role，跨域权限级别的请求，禁止修改主 domain 的 role
            if not role_obj.builtin:
                if (request.privilege_level == 3 and role_obj.domain != request.user.domain) or \
                        (request.privilege_level == 2 and role_obj.domain == request.user.domain):
                    raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要删除的列表
            user_uuid_set = set(user_opts_dict['uuid_list'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', role=role_uuid))
            del_user_uuid_list = list(old_user_uuid_set & user_uuid_set)

            # 删除多对多关系，对于 role 是内置的，不允许跨域权限级别的请求删除主 domain 的 user，
            # 只允许域权限级别的请求删除与登录用户所在 domain 的 user
            for user_uuid in del_user_uuid_list:
                m2m_obj = self.m2m_model.get_obj(role=role_uuid, user=user_uuid)
                try:
                    user_obj = self.user_model.get_obj(uuid=user_uuid)
                except ObjectNotExist:
                    self.m2m_model.delete_obj(m2m_obj)
                else:
                    if role_obj.builtin:
                        if (request.privilege_level == 2 and user_obj.domain == request.user.domain) or \
                                (request.privilege_level == 3 and user_obj.domain != request.user.domain):
                            raise PermissionDenied()
                    self.m2m_model.delete_obj(m2m_obj)

            # 获取关联的 user 列表，对于内置 role，域权限级别的请求，只允许获取登录用户所在 domain 的 user
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            domain_opts = {
                'domain': request.user.domain} if role_obj.builtin and request.privilege_level == 3 else {}
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list, **domain_opts)

            # 返回关联的 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)
