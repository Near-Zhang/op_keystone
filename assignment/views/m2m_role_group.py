from op_keystone.exceptions import CustomException
from identity.views import M2MGroupRoleView


class RoleToGroupView(M2MGroupRoleView):
    """
    通过角色，对将其引用的用户组进行增、删、改、查
    """

    def get(self, request, role_uuid):
        try:
            # 获取最新 group 列表
            self.role_model.get_obj(uuid=role_uuid)
            group_uuid_list = self.m2m_model.get_field_list('group', role=role_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, role_uuid):
        try:
            # 提取参数
            group_opts = ['groups']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要添加的列表
            self.role_model.get_obj(uuid=role_uuid)
            group_uuid_set = set(group_opts_dict['groups'])
            old_group_uuid_set = set(self.m2m_model.get_field_list('group', role=role_uuid))
            add_group_uuid_list = list(group_uuid_set - old_group_uuid_set)

            # 添加多对多关系
            for group_uuid in add_group_uuid_list:
                self.group_model.get_obj(uuid=group_uuid)
                self.m2m_model.create_obj(group=group_uuid, role=role_uuid)

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', role=role_uuid)
            group_dict_list = self.role_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, role_uuid):
        try:
            # 提取参数
            group_opts = ['groups']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要添加和删除的列表
            self.role_model.get_obj(uuid=role_uuid)
            group_uuid_set = set(group_opts_dict['groups'])
            old_group_uuid_set = set(self.m2m_model.get_field_list('group', role=role_uuid))
            add_group_uuid_list = list(group_uuid_set - old_group_uuid_set)
            del_group_uuid_list = list(old_group_uuid_set - group_uuid_set)

            # 添加多对多关系
            for group_uuid in add_group_uuid_list:
                self.group_model.get_obj(uuid=group_uuid)
                self.m2m_model.create_obj(group=group_uuid, role=role_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(role=role_uuid, role__in=del_group_uuid_list).delete()

            # 获取最新 role 列表
            group_uuid_list = self.m2m_model.get_field_list('group', role=role_uuid)
            group_dict_list = self.role_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, role_uuid):
        try:
            # 提取参数
            group_opts = ['groups']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 删除多对多关系
            group_uuid_list = group_opts_dict['groups']
            self.m2m_model.get_obj_qs(role=role_uuid, role__in=group_uuid_list).delete()

            # 获取最新 role 列表
            group_uuid_list = self.m2m_model.get_field_list('group', role=role_uuid)
            group_dict_list = self.role_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)
