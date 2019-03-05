from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils.dao import DAO
from utils import tools


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

    def get(self, request, uuid):
        try:
            # 保证 user 存在
            user_uuid = uuid
            user_obj = self.user_model.get_obj(uuid=user_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and user_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            # 返回最新 group 列表
            data = tools.paging_list(group_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, uuid):
        try:
            # 保证 user 存在
            user_uuid = uuid
            user_obj = self.user_model.get_obj(uuid=user_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and user_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and user_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            group_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要添加的 group uuid 列表
            group_uuid_set = set(group_opts_dict['uuid_list'])
            old_group_uuid_set = set(self.m2m_model.get_field_list('group', user=user_uuid))
            add_group_uuid_list = list(group_uuid_set - old_group_uuid_set)

            # 保证每个 group 存在并和 user 处于一个 domain，然后添加多对多关系
            for group_uuid in add_group_uuid_list:
                self.group_model.get_obj(uuid=group_uuid, domain=user_obj.domain)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            # 返回最新 group 列表
            data = tools.paging_list(group_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, uuid):
        try:
            # 保证 user 存在
            user_uuid = uuid
            user_obj = self.user_model.get_obj(uuid=user_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and user_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and user_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            group_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要添加和删除的 group uuid 列表
            group_uuid_set = set(group_opts_dict['uuid_list'])
            old_group_uuid_set = set(self.m2m_model.get_field_list('group', user=user_uuid))
            add_group_uuid_list = list(group_uuid_set - old_group_uuid_set)
            del_group_uuid_list = list(old_group_uuid_set - group_uuid_set)

            # 保证每个 group 存在并和 user 处于一个 domain，然后添加多对多关系
            for group_uuid in add_group_uuid_list:
                self.group_model.get_obj(uuid=group_uuid, domain=user_obj.domain)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(user=user_uuid, group__in=del_group_uuid_list).delete()

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            # 返回最新 group 列表
            data = tools.paging_list(group_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, uuid):
        try:
            # 保证 user 存在
            user_uuid = uuid
            user_obj = self.user_model.get_obj(uuid=user_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and user_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and user_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            group_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            group_opts_dict = self.extract_opts(request_params, group_opts)

            # 获取需要删除的 group uuid 列表
            group_uuid_list = group_opts_dict['uuid_list']

            # 删除多对多关系
            self.m2m_model.get_obj_qs(user=user_uuid, group__in=group_uuid_list).delete()

            # 获取最新 group 列表
            group_uuid_list = self.m2m_model.get_field_list('group', user=user_uuid)
            group_dict_list = self.group_model.get_dict_list(uuid__in=group_uuid_list)

            # 返回最新 group 列表
            data = tools.paging_list(group_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)


class GroupToUserView(M2MUserGroupView):
    """
    通过用户组，对其包含的用户进行增、删、改、查
    """

    def get(self, request, uuid):
        try:
            # 保证 group 存在
            group_uuid = uuid
            group_obj = self.group_model.get_obj(uuid=group_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and group_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, uuid):
        try:
            # 保证 group 存在
            group_uuid = uuid
            group_obj = self.group_model.get_obj(uuid=group_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and group_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and group_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加的 user uuid 列表
            user_uuid_set = set(user_opts_dict['uuid_list'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', group=group_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)

            # 保证每个 user 存在并和 group 处于一个 domain，然后添加多对多关系
            for user_uuid in add_user_uuid_list:
                self.user_model.get_obj(uuid=user_uuid, domain=group_obj.domain)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, uuid):
        try:
            # 保证 group 存在
            group_uuid = uuid
            group_obj = self.group_model.get_obj(uuid=group_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and group_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and group_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要添加和删除的 user uuid 列表
            user_uuid_set = set(user_opts_dict['uuid_list'])
            old_user_uuid_set = set(self.m2m_model.get_field_list('user', group=group_uuid))
            add_user_uuid_list = list(user_uuid_set - old_user_uuid_set)
            del_user_uuid_list = list(old_user_uuid_set - user_uuid_set)

            # 保证每个 user 存在并和 group 处于一个 domain，然后添加多对多关系
            for user_uuid in add_user_uuid_list:
                self.user_model.get_obj(uuid=user_uuid, domain=group_obj.domain)
                self.m2m_model.create_obj(user=user_uuid, group=group_uuid)

            # 删除多对多关系
            self.m2m_model.get_obj_qs(group=group_uuid, group__in=del_user_uuid_list).delete()

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, uuid):
        try:
            # 保证 group 存在
            group_uuid = uuid
            group_obj = self.group_model.get_obj(uuid=group_uuid)

            # 非跨域权限级别的请求，禁止查询其他 domain 的对象
            if request.privilege_level == 3 and group_obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改涉及主 domain 的对象
            if request.privilege_level == 2 and group_obj.domain == request.user.domain:
                raise PermissionDenied()

            # 提取参数
            user_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            user_opts_dict = self.extract_opts(request_params, user_opts)

            # 获取需要删除的 user uuid 列表
            user_uuid_list = user_opts_dict['uuid_list']

            # 删除多对多关系
            self.m2m_model.get_obj_qs(group=group_uuid, user__in=user_uuid_list).delete()

            # 获取最新 user 列表
            user_uuid_list = self.m2m_model.get_field_list('user', group=group_uuid)
            user_dict_list = self.user_model.get_dict_list(uuid__in=user_uuid_list)

            # 返回最新 user 列表
            data = tools.paging_list(user_dict_list)
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)
