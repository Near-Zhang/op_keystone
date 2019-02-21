from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils.dao import DAO
from utils import tools


class M2MRolePolicyView(BaseView):
    """
    角色和策略的基础多对多视图类
    """

    role_model = DAO('assignment.models.Role')
    policy_model = DAO('assignment.models.Policy')
    m2m_model = DAO('assignment.models.M2MRolePolicy')


class RoleToPolicyView(M2MRolePolicyView):
    """
    通过角色，对其引用的策略进行增、删、改、查
    """

    def get(self, request, role_uuid):
        try:
            # 保证 role 存在
            role_obj = self.role_model.get_obj(uuid=role_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and role_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 获取最新 policy 列表
            policy_uuid_list = self.m2m_model.get_field_list('policy', role=role_uuid)
            policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list)

            # 返回最新 policy 列表
            data = tools.paging_list(policy_dict_list)
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
            policy_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            policy_opts_dict = self.extract_opts(request_params, policy_opts)

            # 获取需要添加的列表
            policy_uuid_set = set(policy_opts_dict['uuid_list'])
            old_policy_uuid_set = set(self.m2m_model.get_field_list('policy', role=role_uuid))
            add_policy_uuid_list = list(policy_uuid_set - old_policy_uuid_set)

            # 保证 policy 存在且是相同 domain 或者是内置，然后添加多对多关系
            for policy_uuid in add_policy_uuid_list:
                try:
                    self.policy_model.get_obj(uuid=policy_uuid, domain=role_obj.domain)
                except ObjectNotExist:
                    self.policy_model.get_obj(uuid=policy_uuid, builtin=True)
                self.m2m_model.create_obj(role=role_uuid, policy=policy_uuid)

            # 获取最新 policy 列表
            policy_uuid_list = self.m2m_model.get_field_list('policy', role=role_uuid)
            policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list)

            # 返回最新 policy 列表
            data = tools.paging_list(policy_dict_list)
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
            policy_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            policy_opts_dict = self.extract_opts(request_params, policy_opts)

            # 获取需要添加和删除的列表
            policy_uuid_set = set(policy_opts_dict['uuid_list'])
            old_policy_uuid_set = set(self.m2m_model.get_field_list('policy', role=role_uuid))
            add_policy_uuid_list = list(policy_uuid_set - old_policy_uuid_set)
            del_policy_uuid_list = list(old_policy_uuid_set - policy_uuid_set)

            # 保证 policy 存在且是相同 domain 或者是内置，然后添加多对多关系
            for policy_uuid in add_policy_uuid_list:
                try:
                    self.policy_model.get_obj(uuid=policy_uuid, domain=role_obj.domain)
                except ObjectNotExist:
                    self.policy_model.get_obj(uuid=policy_uuid, builtin=True)
                self.m2m_model.create_obj(role=role_uuid, policy=policy_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(role=role_uuid, policy__in=del_policy_uuid_list).delete()

            # 获取最新 policy 列表
            policy_uuid_list = self.m2m_model.get_field_list('policy', role=role_uuid)
            policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list)

            # 返回最新 policy 列表
            data = tools.paging_list(policy_dict_list)
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
            policy_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            policy_opts_dict = self.extract_opts(request_params, policy_opts)

            # 删除多对多关系
            policy_uuid_list = policy_opts_dict['uuid_list']
            self.m2m_model.get_obj_qs(role=role_uuid, policy__in=policy_uuid_list).delete()

            # 获取最新 policy 列表
            policy_uuid_list = self.m2m_model.get_field_list('policy', role=role_uuid)
            policy_dict_list = self.policy_model.get_dict_list(uuid__in=policy_uuid_list)

            # 返回最新 policy 列表
            data = tools.paging_list(policy_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)


class PolicyToRoleView(M2MRolePolicyView):
    """
    通过策略，对将其引用的角色进行增、删、改、查
    """

    def get(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and policy_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 获取最新 role 列表
            role_uuid_list = self.m2m_model.get_field_list('role', policy=policy_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and policy_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and policy_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 获取需要添加的列表
            role_uuid_set = set(role_opts_dict['uuid_list'])
            old_role_uuid_set = set(self.m2m_model.get_field_list('role', policy=policy_uuid))
            add_role_uuid_list = list(role_uuid_set - old_role_uuid_set)

            # 保证 role 存在且是相同 domain 或者是内置，然后添加多对多关系
            for role_uuid in add_role_uuid_list:
                try:
                    self.role_model.get_obj(uuid=role_uuid, domain=policy_obj.domain)
                except ObjectNotExist:
                    self.role_model.get_obj(uuid=role_uuid, builtin=True)
                self.m2m_model.create_obj(role=role_uuid, policy=policy_uuid)

            # 获取最新 role 列表
            role_uuid_list = self.m2m_model.get_field_list('role', policy=policy_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and policy_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and policy_obj.domain == request.user.domain:
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

            # 保证 role 存在且是相同 domain 或者是内置，然后添加多对多关系
            for role_uuid in add_role_uuid_list:
                try:
                    self.role_model.get_obj(uuid=role_uuid, domain=policy_obj.domain)
                except ObjectNotExist:
                    self.role_model.get_obj(uuid=role_uuid, builtin=True)
                self.m2m_model.create_obj(role=role_uuid, policy=policy_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(policy=policy_uuid, policy__in=del_role_uuid_list).delete()

            # 获取最新 policy 列表
            role_uuid_list = self.m2m_model.get_field_list('role', policy=policy_uuid)
            role_dict_list = self.policy_model.get_dict_list(uuid__in=role_uuid_list)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, policy_uuid):
        try:
            # 保证 policy 存在
            policy_obj = self.policy_model.get_obj(uuid=policy_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and policy_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and policy_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 删除多对多关系
            role_uuid_list = role_opts_dict['uuid_list']
            self.m2m_model.get_obj_qs(policy=policy_uuid, role__in=role_uuid_list).delete()

            # 获取最新 policy 列表
            role_uuid_list = self.m2m_model.get_field_list('role', policy=policy_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            # 返回最新 role 列表
            data = tools.paging_list(role_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)
