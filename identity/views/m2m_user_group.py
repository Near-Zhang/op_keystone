from op_keystone.exceptions import CustomException
from op_keystone.base_view import BaseView
from utils.dao import DAO


class M2MUserGroupView(BaseView):
    """
    用户和组的基础多对多视图类
    """

    user_model = DAO('identity.models.User')
    group_model = DAO('identity.models.Group')
    m2m_model = DAO('identity.models.M2MUserGroup')


class UserToGroupView(M2MUserGroupView):
    """
    通过用户，对其所属的组进行增、删、改、查
    """

    def get(self, request, user_uuid):
        try:
            # 获取最新 group 列表
            self.user_model.get_obj(uuid=user_uuid)
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, user_uuid):
        try:
            # 提取参数
            group_opts = ['groups']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要添加的列表
            self.user_model.get_obj(uuid=user_uuid)
            group_uuid_set = set(group_opts_dict['groups'])
            old_group_uuid_set = set(self.m2m_model.get_field_list('group', user=user_uuid))
            add_group_uuid_list = list(group_uuid_set - old_group_uuid_set)

            # 添加多对多关系
            for group_uuid in add_group_uuid_list:
                self.group_model.get_obj(uuid=group_uuid)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, user_uuid):
        try:
            # 提取参数
            group_opts = ['groups']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要添加和删除的列表
            self.user_model.get_obj(uuid=user_uuid)
            group_uuid_set = set(group_opts_dict['groups'])
            old_group_uuid_set = set(self.m2m_model.get_field_list('group', user=user_uuid))
            add_group_uuid_list = list(group_uuid_set - old_group_uuid_set)
            del_group_uuid_list = list(old_group_uuid_set - group_uuid_set)

            # 添加多对多关系
            for group_uuid in add_group_uuid_list:
                self.group_model.get_obj(uuid=group_uuid)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(user=user_uuid, group__in=del_group_uuid_list).delete()

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, user_uuid):
        try:
            # 提取参数
            group_opts = ['groups']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 删除多对多关系
            group_uuid_list = group_opts_dict['groups']
            self.m2m_model.get_obj_qs(user=user_uuid, group__in=group_uuid_list).delete()

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            return self.standard_response(group_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)


class GroupToUserView(M2MUserGroupView):
    """
    通过用户组，对其包含的用户进行增、删、改、查
    """

    def get(self, request, group_uuid):
        try:
            # 获取最新 user 列表
            self.group_model.get_obj(uuid=group_uuid)
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            return self.standard_response(user_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, group_uuid):
        try:
            # 提取参数
            user_opts = ['users']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加的列表
            self.group_model.get_obj(uuid=group_uuid)
            user_uuid_set = set(user_opts_dict['users'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', group=group_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)

            # 添加多对多关系
            for user_uuid in add_user_uuid_list:
                self.user_model.get_obj(uuid=user_uuid)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.group_model.get_dict_list(uuid__in=user_uuid_list)

            return self.standard_response(user_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, group_uuid):
        try:
            # 提取参数
            user_opts = ['users']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加和删除的列表
            self.group_model.get_obj(uuid=group_uuid)
            user_uuid_set = set(user_opts_dict['users'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', group=group_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)
            del_user_uuid_list = list(old_user_uuid_set - user_uuid_set)

            # 添加多对多关系
            for user_uuid in add_user_uuid_list:
                self.user_model.get_obj(uuid=user_uuid)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(group=group_uuid, group__in=del_user_uuid_list).delete()

            # 获取最新 group 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.group_model.get_dict_list(uuid__in=user_uuid_list)

            return self.standard_response(user_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, group_uuid):
        try:
            # 提取参数
            user_opts = ['users']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 删除多对多关系
            user_uuid_list = user_opts_dict['users']
            self.m2m_model.get_obj_qs(group=group_uuid, group__in=user_uuid_list).delete()

            # 获取最新 group 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.group_model.get_dict_list(uuid__in=user_uuid_list)

            return self.standard_response(user_dict_list)

        except CustomException as e:
            return self.exception_to_response(e)
