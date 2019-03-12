from op_keystone.exceptions import CustomException, PermissionDenied, RoutingParamsError
from op_keystone.base_view import ResourceView


class ActionsView(ResourceView):
    """
    动作的增、删、改、查
    """

    def __init__(self):
        model = 'assignment.models.Action'
        super().__init__(model)

    def post(self, request, uuid=None):
        try:
            # 非全局权限级别的请求，直接进行权限拒绝
            if request.privilege_level != 1:
                raise PermissionDenied()

            # 定义参数提取列表
            necessary_opts = [
                'name', 'service', 'url',
                'method'
            ]
            extra_opts = [
                'comment'
            ]

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

    def put(self, request, uuid=None):
        try:
            # 非全局权限级别的请求，直接进行权限拒绝
            if request.privilege_level != 1:
                raise PermissionDenied()

            # 若 uuid 不存在，发生路由参数异常，否则获取资源定位对象
            if not uuid:
                raise RoutingParamsError()
            obj = self._model.get_obj(uuid=uuid)

            # 参数提取
            extra_opts = [
                'name', 'service', 'url',
                'method', 'res_location', 'res_key',
                'comment'
            ]
            request_params = self.get_params_dict(request)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象更新
            extra_opts_dict['updated_by'] = request.user.uuid
            check_methods = ('pre_save',)
            updated_obj = self._model.update_obj(obj, check_methods=check_methods, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)
