from op_keystone.exceptions import *
from op_keystone.base_view import ResourceView
from utils import tools
from utils.dao import DAO


class EndpointView(ResourceView):
    """
    端点的增、删、改、查
    """

    def __init__(self):
        model = 'catalog.models.Endpoint'
        super().__init__(model)

    def post(self, request):
        try:
            # 非全局权限级别的请求，直接进行权限拒绝
            if request.privilege_level != 1:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['ip', 'port', 'service']
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
            obj = self.endpoint_model.create_obj(**obj_field)

            # 返回创建的对象
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 非全局权限级别的请求，直接进行权限拒绝
            if request.privilege_level != 1:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['uuid']
            extra_opts = [
                'ip', 'port', 'service',
                'enable', 'comment'
            ]

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象获取
            obj = self.endpoint_model.get_obj(**necessary_opts_dict)

            # 对象更新
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.endpoint_model.update_obj(obj, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request):
        try:
            # 非全局权限级别的请求，直接进行权限拒绝
            if request.privilege_level != 1:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['uuid']

            # 参数获取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 对象删除
            deleted_obj = self.endpoint_model.delete_obj(**necessary_opts_dict)

            # 返回删除的对象
            return self.standard_response('succeed to delete %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
