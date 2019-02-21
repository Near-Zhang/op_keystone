from op_keystone.exceptions import CustomException, PermissionDenied
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO


class DomainsView(BaseView):
    """
    域的查、增、改、删
    """

    domain_model = DAO('partition.models.Domain')

    def get(self, request):
        try:
            # 域权限级别的请求，直接返回当前 domain 信息
            if request.privilege_level == 3:
                obj = self.domain_model.get_obj(uuid=request.user.domain)
                return self.standard_response(obj.serialize())

            # 提取 uuid 参数
            uuid_opts = ['uuid']
            request_params = self.get_params_dict(request, nullable=True)
            uuid_opts_dict = self.extract_opts(request_params, uuid_opts, necessary=False)

            # 若存在 uuid 参数则返回获取的单个对象
            if uuid_opts_dict:
                obj = self.domain_model.get_obj(**uuid_opts_dict)
                return self.standard_response(obj.serialize())

            # 页码参数提取
            page_opts = ['page', 'page-size']
            page_opts_dict = self.extract_opts(request_params, page_opts, necessary=False)

            # 当前页数据获取
            total_list = self.domain_model.get_dict_list()
            page_list = tools.paging_list(total_list, **page_opts_dict)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

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
            obj = self.domain_model.create_obj(check_methods=check_methods, **obj_field)

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
            obj = self.domain_model.get_obj(**necessary_opts_dict)
            check_methods = ('pre_save',)
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.domain_model.update_obj(obj, check_methods=check_methods, **extra_opts_dict)

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
            obj = self.domain_model.get_obj(**necessary_opts_dict)
            check_methods = ('pre_delete',)
            deleted_obj = self.domain_model.delete_obj(obj, check_methods=check_methods)

            # 返回成功删除
            return self.standard_response('succeed to delete domain %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
