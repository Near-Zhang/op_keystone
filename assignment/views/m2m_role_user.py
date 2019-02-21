from op_keystone.exceptions import *
from identity.views import M2MUserRoleView
from utils import tools


class RoleToUserView(M2MUserRoleView):
    """
    通过角色，对将其引用的用户进行增、删、改、查
    """

    def get(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and role_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 获取最新 user 列表，如果登录用户非云管理员，且role 是内置，筛选出当前登录用户相同 domain 的 user
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            if not request.cloud_admin and role_obj.builtin:
                user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list, domain=request.user.domain)
            else:
                user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and role_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and role_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加的列表
            user_uuid_set = set(user_opts_dict['uuid_list'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', role=role_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)

            # 保证 user 存在，当 role 不是内置时，和 role 拥有相同 domain，然后添加多对多关系
            for user_uuid in add_user_uuid_list:
                if role_obj.builtin:
                    self.user_model.get_obj(uuid=user_uuid)
                else:
                    self.user_model.get_obj(uuid=user_uuid, domain=role_obj.domain)
                self.m2m_model.create_obj(user=user_uuid, role=role_uuid)

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and role_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and role_obj.domain == request.user.domain:
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

            # 保证 user 存在，当 role 不是内置时，和 role 拥有相同 domain，然后添加多对多关系
            for user_uuid in add_user_uuid_list:
                if role_obj.builtin:
                    self.user_model.get_obj(uuid=user_uuid)
                else:
                    self.user_model.get_obj(uuid=user_uuid, domain=role_obj.domain)
                self.m2m_model.create_obj(user=user_uuid, role=role_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(role=role_uuid, role__in=del_user_uuid_list).delete()

            # 获取最新 role 列表
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            user_dict_list = self.role_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and role_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and role_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 删除多对多关系
            user_uuid_list = user_opts_dict['uuid_list']
            self.m2m_model.get_obj_qs(role=role_uuid, user__in=user_uuid_list).delete()

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', role=role_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)
