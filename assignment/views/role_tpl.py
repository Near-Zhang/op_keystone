from op_keystone.base_view import BaseView, ResourceView
from op_keystone.exceptions import CustomException
from utils.dao import DAO
from ..models import RoleTpl


class RoleTplsView(ResourceView):
    """
    角色模版的增、删、改、查
    """

    def __init__(self):
        model = RoleTpl
        super().__init__(model)


class TplBasedRole(BaseView):
    """
    使用角色模版来生成角色
    """

    def __init__(self):
        super().__init__()
        self._role_tpl_model = DAO('assignment.models.RoleTpl')
        self._policy_model = DAO('assignment.models.Policy')
        self._role_model = DAO('assignment.models.Role')
        self._m2m_model = DAO('assignment.models.M2MRolePolicy')

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = ['name', 'role_tpl', 'condition_values']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            extra_opts = ['comment', 'domain']
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 结合请求信息，设置到策略 model 属性，
            self._role_tpl_model.combine_request(request)
            self._policy_model.combine_request(request)
            self._role_model.combine_request(request)

            # 模版对象获取
            role_tpl = self._role_tpl_model.get_obj(uuid=necessary_opts_dict['role_tpl']).serialize()

            # 生成条件，策略创建
            domain = extra_opts_dict.get('domain')
            if domain:
                policy_exta_opts = { 'domain': domain }
            else:
                policy_exta_opts = {}

            policy_uuid_list = []
            i = 1
            for a in role_tpl['actions']:
                condition = None
                if a.get('enable_condition'):
                    condition_values = necessary_opts_dict.get('condition_values')
                    if len(condition_values) > 0:
                        condition = a.get('condition_field') + '|'.join(necessary_opts_dict['condition_values'])

                if a.get('effect') and a.get('effect') in ['allow', 'deny'] :
                    effect = a.get('effect')
                else:
                    effect = 'allow'

                policy_fields = {
                    'name': necessary_opts_dict['name'] + ' 的策略' + str(i),
                    'action': a['uuid'],
                    'res': '*',
                    'condition': condition,
                    'effect': effect,
                    'comment' : '为 %s 生成的策略' % necessary_opts_dict['name']
                }
                self._policy_model.get_opts(create=True)
                policy_opts = self._policy_model.validate_opts_dict(policy_fields, policy_exta_opts)
                policy_created = self._policy_model.create_obj(**policy_opts)
                policy_uuid_list.append(policy_created.uuid)
                i += 1

            # 角色创建
            role_fields = {
                'name': necessary_opts_dict['name']
            }
            self._role_model.get_opts(create=True)
            role_opts = self._role_model.validate_opts_dict(role_fields, extra_opts_dict)
            role_created = self._role_model.create_obj(**role_opts)

            # 策略绑定角色
            for p in policy_uuid_list:
                self._m2m_model.create_obj(**{
                    'role': role_created.uuid,
                    'policy': p
                })

            # 返回角色信息
            return self.standard_response(role_created.serialize())

        except CustomException as e:
            return self.exception_to_response(e)