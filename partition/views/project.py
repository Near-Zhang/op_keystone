from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO


class ProjectsView(BaseView):
    """
    项目的增、删、改、查
    """

    project_model = DAO('partition.models.Project')

    def get(self, request):
        try:
            # 域权限级别的请求设置 domain 字段过滤参数
            if request.privilege_level == 3:
                domain_opts_dict = {'domain': request.user.domain}
            else:
                domain_opts_dict = {}

            # 获取 uuid 参数
            uuid_opts = ['uuid']
            request_params = self.get_params_dict(request, nullable=True)
            uuid_opts_dict = self.extract_opts(request_params, uuid_opts, necessary=False)

            # 若存在 uuid 参数则返回获取的单个对象
            if uuid_opts_dict:
                obj = self.project_model.get_obj(**uuid_opts_dict, **domain_opts_dict)
                return self.standard_response(obj.serialize())

            # 获取多个对象，提取页码参数
            page_opts = ['page', 'page-size']
            request_params = self.get_params_dict(request, nullable=True)
            page_opts_dict = self.extract_opts(request_params, page_opts, necessary=False)

            # 当前页数据获取
            total_list = self.project_model.get_dict_list(**domain_opts_dict)
            page_list = tools.paging_list(total_list, **page_opts_dict)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request):
        try:
            # 定义参数提取列表
            necessary_opts = ['name']
            extra_opts = ['enable', 'comment']

            # 非域权限级别的请求，进行参数提取列表补充
            if request.privilege_level < 3:
                extra_opts.extend([
                    'domain'
                ])

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 跨域权限级别的请求，禁止操作主 domain
            if request.privilege_level == 2:
                if necessary_opts_dict['domain'] == request.user.domain:
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
            obj = self.project_model.create_obj(check_methods=check_methods, **obj_field)

            # 返回创建的对象
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request):
        try:
            # 定义参数提取列表
            necessary_opts = ['uuid']
            extra_opts = [
                'name', 'enable', 'comment']

            # 非域权限级别的请求，进行参数提取列表补充，否则设置 domain 字段过滤参数
            if request.privilege_level < 3:
                domain_opts_dict = {}
                extra_opts.extend([
                    'domain'
                ])
            else:
                domain_opts_dict = {'domain': request.user.domain}

            # 参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 跨域权限级别的请求，禁止操作主 domain
            if request.privilege_level == 2:
                if necessary_opts_dict['domain'] == request.user.domain:
                    raise PermissionDenied()

            # 对象获取
            obj = self.project_model.get_obj(**necessary_opts_dict, **domain_opts_dict)

            # 对象更新
            check_methods = ('pre_save',)
            extra_opts_dict['updated_by'] = request.user.uuid
            updated_obj = self.project_model.update_obj(obj, check_methods=check_methods, **extra_opts_dict)

            # 返回更新的对象
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request):
        try:
            # 域权限级别的请求，设置 domain 字段过滤参数
            if request.privilege_level < 3:
                domain_opts_dict = {}
            else:
                domain_opts_dict = {'domain': request.user.domain}

            # 参数获取
            necessary_opts = ['uuid']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 跨域权限级别的请求，禁止操作主 domain
            if request.privilege_level == 2:
                if necessary_opts_dict['domain'] == request.user.domain:
                    raise PermissionDenied()

            # 对象删除
            deleted_obj = self.project_model.delete_obj(**necessary_opts_dict, **domain_opts_dict)

            # 返回成功删除
            return self.standard_response('succeed to delete %s' % deleted_obj.name)

        except CustomException as e:
            return self.exception_to_response(e)
