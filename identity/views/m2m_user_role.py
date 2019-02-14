from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils.dao import DAO


class M2MUserRoleView(BaseView):
    """
    用户和角色的基础多对多视图类
    """

    user_model = DAO('identity.models.User')
    role_model = DAO('assignment.models.Role')
    m2m_model = DAO('identity.models.M2MUserRole')


class UserToRoleView(M2MUserRoleView):
    """
    通过用户，对其所属的角色进行增、删、改、查
    """

    def get(self, request, user_uuid):
        try:
            # 保证 user 存在
            self.user_model.get_obj(uuid=user_uuid)

            # 获取最新 role 列表
            role_uuid_list = self.m2m_model.get_field_list('role', user=user_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            return self.standard_response(role_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, user_uuid):
        try:
            # 保证 user 存在
            user_obj = self.user_model.get_obj(uuid=user_uuid)

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 获取需要添加的列表
            role_uuid_set = set(role_opts_dict['uuid_list'])
            old_role_uuid_set = set(self.m2m_model.get_field_list('role', user=user_uuid))
            add_role_uuid_list = list(role_uuid_set - old_role_uuid_set)

            # 保证角色是同 domain 或者是内置，然后添加多对多关系
            for role_uuid in add_role_uuid_list:
                try:
                    self.role_model.get_obj(uuid=role_uuid, domain=user_obj.domain)
                except ObjectNotExist:
                    self.role_model.get_obj(uuid=role_uuid, builtin=True)
                self.m2m_model.create_obj(user=user_uuid, role=role_uuid)

            # 获取最新 role 列表
            role_uuid_list = self.m2m_model.get_field_list('role', user=user_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            return self.standard_response(role_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, user_uuid):
        try:
            # 保证 user 存在
            user_obj = self.user_model.get_obj(uuid=user_uuid)

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 获取需要添加和删除的列表
            role_uuid_set = set(role_opts_dict['uuid_list'])
            old_role_uuid_set = set(self.m2m_model.get_field_list('role', user=user_uuid))
            add_role_uuid_list = list(role_uuid_set - old_role_uuid_set)
            del_role_uuid_list = list(old_role_uuid_set - role_uuid_set)

            # 保证角色是同 domain 或者是内置，然后添加多对多关系
            for role_uuid in add_role_uuid_list:
                try:
                    self.role_model.get_obj(uuid=role_uuid, domain=user_obj.domain)
                except ObjectNotExist:
                    self.role_model.get_obj(uuid=role_uuid, builtin=True)
                self.m2m_model.create_obj(user=user_uuid, role=role_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(user=user_uuid, role__in=del_role_uuid_list).delete()

            # 获取最新 role 列表
            role_uuid_list = self.m2m_model.get_field_list('role', user=user_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            return self.standard_response(role_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, user_uuid):
        try:
            # 保证 user 存在
            self.user_model.get_obj(uuid=user_uuid)

            # 提取参数
            role_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            role_opts_dict = self.extract_opts(request_params, role_opts)

            # 删除多对多关系
            del_role_uuid_list = role_opts_dict['uuid_list']
            self.m2m_model.get_obj_qs(user=user_uuid, role__in=del_role_uuid_list).delete()

            # 获取最新 role 列表
            role_uuid_list = self.m2m_model.get_field_list('role', user=user_uuid)
            role_dict_list = self.role_model.get_dict_list(uuid__in=role_uuid_list)

            return self.standard_response(role_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)
