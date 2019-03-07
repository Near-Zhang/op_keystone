from op_keystone.exceptions import CustomException, PermissionDenied
from op_keystone.base_view import ResourceView
from utils import tools
from utils.dao import DAO


class DomainsView(ResourceView):
    """
    域的查、增、改、删
    """

    def __init__(self, **kwargs):
        model = 'partition.models.Domain'
        super().__init__(model, **kwargs)

    def post(self, request):
        try:
            # 域权限级别的请求，直接进行权限拒绝
            if request.privilege_level == 3:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['name', 'company', 'agent']
            extra_opts = ['enable', 'comment']

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 参数合成，预设 create_by 的值
            obj_field = {
                'created_by': request.user.uuid
            }
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)

            # 对象创建
            check_methods = ('pre_save',)
            obj = self._model.create_obj(check_methods=check_methods, **obj_field)

            # 返回创建的对象
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 域权限级别的请求，直接进行权限拒绝
            if request.privilege_level == 3:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = ['uuid']
            extra_opts = [
                'name', 'company', 'enable',
                'comment', 'agent'
            ]

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 跨域权限级别的请求，禁止修改主 domain
            if request.privilege_level == 2 and necessary_opts_dict['uuid'] == request.user.domain:
                raise PermissionDenied()

            # 对象获取并更新
            obj = self._model.get_obj(**necessary_opts_dict)
            check_methods = ('pre_save',)
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self._model.update_obj(obj, check_methods=check_methods, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request):
        try:
            # 域权限级别的请求，直接进行权限拒绝
            if request.privilege_level == 3:
                raise PermissionDenied()

            # 参数提取
            necessary_opts = ['uuid']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 跨域权限级别的请求，禁止操作主 domain
            if request.privilege_level == 2 and necessary_opts_dict['uuid'] == request.user.domain:
                raise PermissionDenied()

            # 对象获取并删除
            obj = self._model.get_obj(**necessary_opts_dict)
            check_methods = ('pre_delete',)
            deleted_obj = self._model.delete_obj(obj, check_methods=check_methods)

            # 返回成功删除
            return self.standard_response('succeed to delete domain %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
