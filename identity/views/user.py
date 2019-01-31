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
            # 设置 domain 字段过滤参数
            if request.user_level == 2:
                domain_opts_dict = {}
            else:
                domain_opts_dict = {'domain': request.user.domain}

            # 提取 uuid 参数
            uuid_opts = ['uuid']
            request_params = self.get_params_dict(request, nullable=True)
            uuid_opts_dict = self.extract_opts(request_params, uuid_opts, necessary=False)

            # 若存在 uuid 参数则返回获取的单个对象
            if uuid_opts_dict:
                obj = self.user_model.get_obj(**uuid_opts_dict, **domain_opts_dict)
                return self.standard_response(obj.serialize())

            # 获取多个对象，提取页码参数
            page_opts = ['page', 'pagesize']
            page_opts_dict = self.extract_opts(request_params, page_opts, necessary=False)

            # 根据页码参数获取当前页的数据列表
            total_list = self.user_model.get_dict_list(**domain_opts_dict)
            page_list = tools.paging_list(total_list, **page_opts_dict)

            # 返回数据列表
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request):
        try:
            # 定义参数提取列表
            necessary_opts = [
                'username','password','name',
                'email', 'phone'
            ]
            extra_opts = [
                'qq', 'comment', 'enable',
            ]

            # 云管理员的参数提取列表补充
            if request.user_level == 2:
                extra_opts.extend([
                    'domain', 'is_main'
                ])

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 参数合成，预设 domain 的值
            obj_field = {'domain': request.user.domain}
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)
            obj_field['created_by'] = request.user.uuid

            # 自检方法执行后，创建用户对象，并创建其用户行为对象
            check_methods = ('check_single_main_user', 'validate_password')
            obj = self.user_model.create_obj(check_methods=check_methods, **obj_field)
            self.user_behavior_model.create_obj(uuid=obj.uuid)

            # 返回创建的对象
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 定义参数提取列表
            necessary_opts = ['uuid']
            extra_opts = [
                'name', 'email', 'phone',
                'qq', 'comment', 'enable'
            ]

            # 设置 domain 字段过滤参数和云管理员的参数提取列表补充
            if request.user_level == 2:
                domain_opts_dict = {}
                extra_opts.extend([
                    'domain', 'is_main'
                ])
            else:
                domain_opts_dict = {'domain': request.user.domain}

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象获取
            obj = self.user_model.get_obj(**necessary_opts_dict, **domain_opts_dict)

            # 对象更新
            check_methods = ('check_single_main_user',)
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.user_model.update_obj(obj, check_methods=check_methods, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request):
        try:
            # 设置 domain 字段过滤参数
            if request.user_level == 2:
                domain_opts_dict = {}
            else:
                domain_opts_dict = {'domain': request.user.domain}

            # 参数获取
            necessary_opts = ['uuid']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 对象软删除
            obj = self.user_model.get_obj(**necessary_opts_dict, **domain_opts_dict)
            soft_deleted_dict = {
                'deleted_time': tools.get_datetime_with_tz(),
                'deleted_by': request.user.uuid
            }
            deleted_obj = self.user_model.update_obj(obj, **soft_deleted_dict)

            return self.standard_response('succeed to delete %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)



