from op_keystone.exceptions import CustomException
from op_keystone.baseview import BaseView
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
            # 页码参数提取
            page_opts = ['page', 'pagesize']
            request_params = self.get_params_dict(request, nullable=True)
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
            obj_field['password'] = tools.password_to_hash(obj_field['password'])

            # 创建用户对象，并创建其行为对象
            ins = self.user_model.create_obj(**obj_field)
            self.user_behavior_model.create_obj(uuid=ins.uuid)

            return self.standard_response(ins.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 参数提取
            necessary_opts = ['uuid']
            extra_opts = [
                'password', 'name', 'email',
                'phone', 'qq', 'comment',
                'enable', 'is_main'
            ]
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象获取
            obj = self.user_model.get_object(**necessary_opts_dict)

            # 对象更新
            password = extra_opts_dict.get('password')
            if password:
                extra_opts_dict['password'] = tools.password_to_hash(password)
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

            # 对象获取
            obj = self.user_model.get_object(**necessary_opts_dict)
            behavior_obj = self.user_behavior_model.get_object(**necessary_opts_dict)

            # 对象删除
            deleted_obj = self.user_model.delete_obj(obj)
            self.user_behavior_model.delete_obj(behavior_obj)

            return self.standard_response(deleted_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)
