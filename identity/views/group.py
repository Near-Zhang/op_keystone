from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO


class GroupsView(BaseView):
    """
    用户组的增、删、改、查
    """

    _model = DAO('identity.models.Group')

    def get(self, request, uuid=None):
        try:
            # 域权限级别的请求，设置 domain 字段过滤参数
            if request.privilege_level == 3:
                domain_opts_dict = {'domain': request.user.domain}
            else:
                domain_opts_dict = {}

            # 若存在路由参数 uuid 则返回获取的单个对象
            if uuid:
                obj = self._model.get_obj(uuid=uuid, **domain_opts_dict)
                return self.standard_response(obj.serialize())

            # 参数提取
            extra_opts = ['query', 'page', 'page-size']
            request_params = self.get_params_dict(request, nullable=True)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 查询对象生成
            query_str = extra_opts_dict.pop('query', None)
            query_obj = DAO.parsing_query_str(query_str)

            # 当前页数据获取
            total_list = self._model.get_dict_list(query_obj, **domain_opts_dict)
            page_list = tools.paging_list(total_list, **extra_opts_dict)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request,  uuid=None):
        try:
            # 定义参数提取列表
            necessary_opts = ['name']
            extra_opts = ['comment', 'enable']

            # 非域权限级别的请求，进行参数提取列表补充
            if request.privilege_level < 3:
                extra_opts.extend([
                    'domain'
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

            # 对象创建
            check_methods = ('pre_save',)
            obj = self._model.create_obj(check_methods=check_methods, **obj_field)

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
            extra_opts = ['name', 'comment', 'enable']

            # 非域权限级别的请求，进行参数提取列表补充
            if request.privilege_level < 3:
                extra_opts.extend([
                    'domain'
                ])

            # 参数提取并获取对象
            request_params = self.get_params_dict(request)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 域权限级别的请求，禁止修改前后涉及其他 domain 的对象
            if request.privilege_level == 3 and obj.domain != request.user.domain:
                raise PermissionDenied()

            # 跨域权限级别的请求，禁止修改前后涉及主 domain 的对象
            if request.privilege_level == 2:
                if extra_opts_dict.get('domain') == request.user.domain or obj.domain == request.user.domain:
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

            # 对象删除
            check_methods = ('pre_delete',)
            deleted_obj = self._model.delete_obj(obj, check_methods=check_methods)

            # 返回成功删除
            return self.standard_response('success to delete %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
