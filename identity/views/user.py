from op_keystone.exceptions import CustomException, PermissionDenied, RoutingParamsError
from op_keystone.base_view import ResourceView
from utils.dao import DAO


class UsersView(ResourceView):
    """
    用户的增、删、改、查
    """

    def __init__(self):
        model = 'identity.models.User'
        super().__init__(model)

    def post(self, request, uuid=None):
        try:
            # 定义参数提取列表
            necessary_opts = [
                'username','password','name',
                'email', 'phone'
            ]
            extra_opts = [
                'qq', 'comment', 'enable',
            ]

            # 非域权限级别的请求，进行参数提取列表补充
            if request.privilege_level < 3:
                extra_opts.extend([
                    'domain', 'is_main'
                ])

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 跨域权限级别的请求，禁止创建涉及主 domain 的对象
            if request.privilege_level == 2:
                if extra_opts_dict.get('domain') is None or extra_opts_dict.get('domain') == request.user.domain:
                    raise PermissionDenied()

            # 参数合成，预设 domain、create_by 的值
            obj_field = {
                'domain': request.user.domain,
                'created_by': request.user.uuid
            }
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)

            # 用户对象创建，然后用户行为对象创建
            check_methods = ('pre_save', 'validate_password')
            obj = self._model.create_obj(check_methods=check_methods, **obj_field)
            self._behavior_model.create_obj(user=obj.uuid)

            # 返回创建的对象
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, uuid=None):
        try:
            # 若 uuid 不存在，发生路由参数异常，否则获取对象
            if not uuid:
                raise RoutingParamsError()
            obj = self._model.get_obj(uuid=uuid)

            # 定义参数提取列表
            extra_opts = [
                'name', 'email', 'phone',
                'qq', 'comment', 'enable'
            ]

            # 非域权限级别的请求，进行参数提取列表补充
            if request.privilege_level < 3:
                extra_opts.extend([
                    'domain', 'is_main'
                ])

            # 参数提取并获取对象
            request_params = self.get_params_dict(request)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 域权限级别的请求，禁止修改前后涉及其他 domain 的对象
            if request.privilege_level == 3 and obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改前后涉及主 domain 的对象
            if request.privilege_level == 2:
                if obj.domain == request.user.domain or extra_opts_dict.get('domain') == request.user.domain:
                    raise PermissionDenied()

            # 对象更新
            check_methods = ('pre_save',)
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self._model.update_obj(obj, check_methods=check_methods, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, uuid=None):
        try:
            # 若 uuid 不存在，发生路由参数异常，否则获取对象
            if not uuid:
                raise RoutingParamsError()
            obj = self._model.get_obj(uuid=uuid)

            # 域权限级别的请求，禁止删除涉及其他 domain 的对象
            if request.privilege_level == 3 and obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止删除涉及主 domain 的对象
            if request.privilege_level == 2 and obj.domain == request.user.domain:
                raise PermissionDenied()

            # 对象软删除
            check_methods = ('pre_delete',)
            deleted_obj = self._model.delete_obj(obj, check_methods=check_methods, deleted_by=request.user.uuid)

            # 返回成功删除
            return self.standard_response('success to delete user %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
