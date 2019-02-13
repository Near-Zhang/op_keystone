from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO


class ServicesView(BaseView):
    """
    服务的增、删、改、查
    """

    service_model = DAO('catalog.models.Service')

    def get(self, request):
        try:
            # 提取 uuid 参数
            uuid_opts = ['uuid']
            request_params = self.get_params_dict(request, nullable=True)
            uuid_opts_dict = self.extract_opts(request_params, uuid_opts, necessary=False)

            # 若存在 uuid 参数则返回获取的单个对象
            if uuid_opts_dict:
                obj = self.service_model.get_obj(**uuid_opts_dict)
                return self.standard_response(obj.serialize())

            # 页码参数提取
            page_opts = ['page', 'pagesize']
            page_opts_dict = self.extract_opts(request_params, page_opts, necessary=False)

            # 当前页数据列获取
            total_list = self.service_model.get_dict_list()
            page_list = tools.paging_list(total_list, **page_opts_dict)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request):
        try:
            # 非云管理员直接进行权限拒绝
            if not request.cloud_admin:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['name', 'function']
            extra_opts = ['comment', 'enable']

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 参数合成
            obj_field = {
                'created_by': request.user.uuid
            }
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)

            # 创建对象
            obj = self.service_model.create_obj(**obj_field)

            # 返回创建的对象
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 非云管理员直接进行权限拒绝
            if not request.cloud_admin:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['uuid']
            extra_opts = [
                'name', 'function', 'enable',
                'comment'
            ]

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象获取
            obj = self.service_model.get_obj(**necessary_opts_dict)

            # 对象更新
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.service_model.update_obj(obj, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request):
        try:
            # 非云管理员直接进行权限拒绝
            if not request.cloud_admin:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['uuid']

            # 参数获取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 对象删除
            deleted_obj = self.service_model.delete_obj(**necessary_opts_dict)

            # 返回删除成功
            return self.standard_response('succeed to delete %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
