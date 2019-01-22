from op_keystone.exceptions import CustomException
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO


class UsersView(BaseView):
    """
    用户的增、删、改、查
    """

    user_model = DAO('identity.models.User')
    user_behavior_model = DAO('identity.models.UserBehavior')

    def get(self, request):
        try:
            # 获取 uuid 参数，若有则为单个对象获取
            uuid_opts = ['uuid']
            request_params = self.get_params_dict(request, nullable=True)
            uuid_opts_dict = self.extract_opts(request_params, uuid_opts, necessary=False)

            if uuid_opts_dict:
                obj = self.user_model.get_obj(**uuid_opts_dict)
                return self.standard_response(obj.serialize())

            # 页码参数提取
            page_opts = ['page', 'pagesize']
            page_opts_dict = self.extract_opts(request_params, page_opts, necessary=False)

            # 当前页数据列获取
            total_list = self.user_model.get_dict_list()
            page_list = tools.paging_list(total_list, **page_opts_dict)

            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = [
                'username', 'domain', 'password',
                'name', 'email', 'phone'
            ]
            extra_opts = [
                'qq', 'comment', 'enable',
                'is_main'
            ]
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 参数合成
            obj_field = {}
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)
            obj_field['created_by'] = request.user.uuid

            # 创建用户对象，并创建其行为对象，密码需要处理
            obj = self.user_model.model(**obj_field)
            obj.validate_password()
            self.user_model.save(obj)
            self.user_behavior_model.create_obj(uuid=obj.uuid)

            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 参数提取
            necessary_opts = ['uuid']
            extra_opts = [
                'is_main', 'name', 'email',
                'phone', 'qq', 'comment',
                'enable'
            ]
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象获取
            obj = self.user_model.get_obj(**necessary_opts_dict)

            # 对象更新
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.user_model.update_obj(obj, **extra_opts_dict)

            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request):
        try:
            # 参数获取
            necessary_opts = ['uuid']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 对象软删除
            obj = self.user_model.get_obj(**necessary_opts_dict)
            soft_deleted_dict = {
                'deleted_time': tools.get_datetime_with_tz(),
                'deleted_by': request.user.uuid
            }
            deleted_obj = self.user_model.update_obj(obj, **soft_deleted_dict)

            return self.standard_response('succeed to delete %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)



