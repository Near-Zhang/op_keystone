from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO
from django.conf import settings


class RoleView(BaseView):
    role_model = DAO('assignment.models.Policy')
    domain_model = DAO('partition.models.Domain')

    def get(self, request):
        pass

    def post(self, request):
        try:
            request_params = self.get_params_dict(request)
            necessary_opts = ['name', 'domain']
            extra_opts = ['enable', 'comment']
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 参数合成
            obj_field = {}
            obj_field.update(necessary_opts_dict)
            obj_field.update(extra_opts_dict)
            obj_field['created_by'] = request.user.uuid
            # 创建对象
            ins = self.domain_model.create_obj(**obj_field)
            return self.standard_response(ins.serialize())

        except CustomException as e:
            return self.exception_to_response(e)


