from op_keystone.exceptions import CustomException
from op_keystone.baseview import BaseView
from utils import tools
from utils.dao import DAO


class GroupsView(BaseView):
    """
    用户组的增、删、改、查
    """

    group_model = DAO('identity.models.Group')

    def get(self, request):
        try:
            # 获取 uuid 参数，若有则为单个对象获取
            uuid_opts = ['uuid']
            request_params = self.get_params_dict(request, nullable=True)
            uuid_opts_dict = self.extract_opts(request_params, uuid_opts, necessary=False)

            if uuid_opts_dict:
                obj = self.group_model.get_object(**uuid_opts_dict)
                return self.standard_response(obj.serialize())

            # 页码参数提取
            page_opts = ['page', 'pagesize']
            page_opts_dict = self.extract_opts(request_params, page_opts, necessary=False)

            # 当前页数据列获取
            total_list = self.group_model.get_dict_list()
            page_list = tools.paging_list(total_list, **page_opts_dict)

            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = ['name', 'domain']
            extra_opts = ['comment', 'enable']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 参数合成
            obj_field = {}
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)
            print(request.user)
            obj_field['created_by'] = request.user.uuid

            # 创建用户对象
            obj = self.group_model.create_obj(**obj_field)

            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 参数提取
            necessary_opts = ['uuid']
            extra_opts = ['name', 'comment', 'enable']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象获取
            obj = self.group_model.get_object(**necessary_opts_dict)

            # 对象更新
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.group_model.update_obj(obj, **extra_opts_dict)

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
            obj = self.group_model.get_object(**necessary_opts_dict)

            # 对象删除
            deleted_obj = self.group_model.delete_obj(obj)

            return self.standard_response(deleted_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)