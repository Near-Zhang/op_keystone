from op_keystone.base_view import BaseView, ResourceView
from op_keystone.exceptions import CustomException, RoutingParamsError, RequestParamsError
from utils.dao import DAO
from ..models import RoleTpl
from utils.tools import json_loader


class RoleTplsView(ResourceView):
    """
    角色模版的增、删、改、查
    """

    def __init__(self):
        model = RoleTpl
        super().__init__(model)


class TplBasedRole(BaseView):
    """
    使用角色模版来生成角色、更新角色、删除角色模版生成的角色
    """

    def __init__(self):
        super().__init__()
        self._role_tpl_model = DAO('assignment.models.RoleTpl')
        self._policy_model = DAO('assignment.models.Policy')
        self._role_model = DAO('assignment.models.Role')
        self._action_model = DAO('assignment.models.Action')
        self._m2m_model = DAO('assignment.models.M2MRolePolicy')

    def post(self, request, uuid=None):
        try:
            # 参数提取
            necessary_opts = ['name', 'role_tpl', 'condition_values']
            if hasattr(request, "service"):
                necessary_opts += 'created_by'
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            extra_opts = ['comment', 'domain']
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 结合请求信息，设置到策略 model 属性，
            self._role_tpl_model.combine_request(request)
            self._policy_model.combine_request(request)
            self._role_model.combine_request(request)
            self._action_model.combine_request(request)

            # 参数和模版对象获取
            tpl_uuid = necessary_opts_dict['role_tpl']
            condition_values = necessary_opts_dict.get('condition_values')
            role_tpl = self._role_tpl_model.get_obj(uuid=tpl_uuid).serialize()

            # 角色创建
            role_fields = {
                'name': necessary_opts_dict['name'],
                'tpl': tpl_uuid,
                'tpl_condition_values': condition_values
            }
            self._role_model.get_opts(create=True)
            role_opts = self._role_model.validate_opts_dict(role_fields, extra_opts_dict)
            role_created = self._role_model.create_obj(**role_opts)

            # 生成条件，策略创建
            extra_opts_dict.pop('comment', None)
            policy_uuid_list = []
            for a in role_tpl['actions']:
                condition = ""
                if a.get('enable_condition') and condition_values:
                        condition = a.get('condition_field') + ':' + '|'.join(condition_values)

                if a.get('effect') and a.get('effect') in ['allow', 'deny'] :
                    effect = a.get('effect')
                else:
                    effect = 'allow'

                action_obj = self._action_model.get_obj(uuid=a['uuid'])

                policy_fields = {
                    'name': '%s 对于 %s 的策略' % (role_created.name, action_obj.name),
                    'action': a['uuid'],
                    'res': '*',
                    'condition': condition,
                    'effect': effect,
                    'comment' : '%s 对于 %s 的策略' % (role_created.name, action_obj.name),
                    'role_based_tpl': role_created.uuid,
                }
                self._policy_model.get_opts(create=True)
                policy_opts = self._policy_model.validate_opts_dict(policy_fields, extra_opts_dict)
                policy_created = self._policy_model.create_obj(**policy_opts)
                policy_uuid_list.append(policy_created.uuid)

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

    def put(self, request, uuid):
        """
        相当于删除并重新生成基于模版角色的策略
        """
        try:
            # 参数提取
            necessary_opts = []
            if hasattr(request, "service"):
                necessary_opts += 'created_by'
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            extra_opts = ['role_tpl', 'condition_values', 'domain']
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 结合请求信息，设置 model 查询参数
            self._role_tpl_model.combine_request(request)
            self._policy_model.combine_request(request)
            self._role_model.combine_request(request)
            self._action_model.combine_request(request)

            # 若 uuid 不存在，发生路由参数异常，否则获取对象，并校验对象权限
            if not uuid:
                raise RoutingParamsError()

            # 保证源对象存在，校验对象权限合法性
            role_obj = self._role_model.get_obj(uuid=uuid)
            self._role_model.validate_obj(role_obj)

            # 模版对象获取
            role_tpl_uuid = extra_opts_dict.pop('role_tpl', None)
            if not role_tpl_uuid:
                role_tpl_uuid = role_obj.tpl
            role_tpl = self._role_tpl_model.get_obj(uuid=role_tpl_uuid).serialize()

            # 模版条件获取
            condition_values = extra_opts_dict.pop('condition_values', None)
            if not condition_values:
                condition_values = json_loader(role_obj.tpl_condition_values)

            # 获取 role 关联 policy 对象的 uuid 列表，删除关联
            del_policy_uuid_list = self._m2m_model.get_field_list('policy', role=uuid)
            self._m2m_model.delete_obj_qs(role=uuid)

            # 判断策略是否是模版生成，是则删除策略
            for p_uuid in del_policy_uuid_list:
                p_obj = self._policy_model.get_obj(uuid=p_uuid)
                if p_obj.role_based_tpl == uuid:
                    self._policy_model.delete_obj(p_obj)

            # 生成条件，策略创建
            policy_uuid_list = []
            for a in role_tpl['actions']:
                condition = ""
                if a.get('enable_condition') and condition_values:
                    condition = a.get('condition_field') + ':' + '|'.join(condition_values)

                if a.get('effect') and a.get('effect') in ['allow', 'deny']:
                    effect = a.get('effect')
                else:
                    effect = 'allow'

                action_obj = self._action_model.get_obj(uuid=a['uuid'])

                policy_fields = {
                    'name': '%s 对于 %s 的策略' % (role_obj.name, action_obj.name),
                    'action': a['uuid'],
                    'res': '*',
                    'condition': condition,
                    'effect': effect,
                    'comment': '%s 对于 %s 的策略' % (role_obj.name, action_obj.name),
                    'role_based_tpl': role_obj.uuid,
                    'domain': role_obj.domain
                }
                self._policy_model.get_opts(create=True)
                policy_opts = self._policy_model.validate_opts_dict(policy_fields, necessary_opts_dict, extra_opts_dict)
                policy_created = self._policy_model.create_obj(**policy_opts)
                policy_uuid_list.append(policy_created.uuid)

            # 策略绑定角色
            for p in policy_uuid_list:
                self._m2m_model.create_obj(**{
                    'role': role_obj.uuid,
                    'policy': p
                })

            # 更新角色
            role_fields = {
                'tpl': role_tpl_uuid,
                'tpl_condition_values': condition_values,
            }
            self._role_model.get_opts()
            role_opts = self._role_model.validate_opts_dict(role_fields, necessary_opts_dict, extra_opts_dict)
            updated_role_obj = self._role_model.update_obj(role_obj, **role_opts)

            # 返回角色信息
            return self.standard_response(updated_role_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, uuid):
        try:
            # 结合请求信息，设置 model 查询参数
            self._role_model.combine_request(request)
            self._policy_model.combine_request(request)

            # 若 uuid 不存在，发生路由参数异常，否则获取对象，并校验对象权限
            if not uuid:
                raise RoutingParamsError()

            # 保证源对象存在，校验对象权限合法性
            role_obj = self._role_model.get_obj(uuid=uuid)
            if not role_obj.tpl:
                raise RequestParamsError(opt="uuid", invalid=True)
            self._role_model.validate_obj(role_obj)

            # 获取 role 关联 policy 对象的 uuid 列表，删除关联
            del_policy_uuid_list = self._m2m_model.get_field_list('policy', role=uuid)
            self._m2m_model.delete_obj_qs(role=uuid)

            # 判断策略是否是模版生成，是则删除策略
            for p_uuid in del_policy_uuid_list:
                p_obj = self._policy_model.get_obj(uuid=p_uuid)
                if p_obj.role_based_tpl == uuid:
                    self._policy_model.delete_obj(p_obj)

            # 删除角色并返回删除信息
            deleted_message = self._role_model.delete_obj(role_obj)
            return self.standard_response(deleted_message)

        except CustomException as e:
            return self.exception_to_response(e)


class TplFlushRole(BaseView):
    """
    使用模版刷新所有所创的角色
    """

    def __init__(self):
        super().__init__()
        self._role_tpl_model = DAO('assignment.models.RoleTpl')
        self._policy_model = DAO('assignment.models.Policy')
        self._role_model = DAO('assignment.models.Role')
        self._action_model = DAO('assignment.models.Action')
        self._m2m_model = DAO('assignment.models.M2MRolePolicy')

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = ['role_tpl']
            if hasattr(request, "service"):
                necessary_opts += 'created_by'
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 结合请求信息，设置到策略 model 属性，
            self._role_tpl_model.combine_request(request)
            self._policy_model.combine_request(request)
            self._role_model.combine_request(request)
            self._action_model.combine_request(request)

            # 模版对象获取
            role_tpl_uuid = necessary_opts_dict.pop('role_tpl')
            role_tpl = self._role_tpl_model.get_obj(uuid=role_tpl_uuid).serialize()

            # 获取所有模版角色
            role_obj_qs = self._role_model.get_obj_qs(tpl=role_tpl['uuid'])

            for role_obj in role_obj_qs:
                # 模版条件获取
                condition_values = json_loader(role_obj.tpl_condition_values)

                # 获取 role 关联 policy 对象的 uuid 列表，删除关联
                del_policy_uuid_list = self._m2m_model.get_field_list('policy', role=role_obj.uuid)
                self._m2m_model.delete_obj_qs(role=role_obj.uuid)

                # 判断策略是否是模版生成，是则删除策略
                for p_uuid in del_policy_uuid_list:
                    p_obj = self._policy_model.get_obj(uuid=p_uuid)
                    if p_obj.role_based_tpl == role_obj.uuid:
                        self._policy_model.delete_obj(p_obj)

                # 生成条件，策略创建
                policy_uuid_list = []
                for a in role_tpl['actions']:
                    condition = ""
                    if a.get('enable_condition') and condition_values:
                        condition = a.get('condition_field') + ':' + '|'.join(condition_values)

                    if a.get('effect') and a.get('effect') in ['allow', 'deny']:
                        effect = a.get('effect')
                    else:
                        effect = 'allow'

                    action_obj = self._action_model.get_obj(uuid=a['uuid'])

                    policy_fields = {
                        'name': '%s 对于 %s 的策略' % (role_obj.name, action_obj.name),
                        'action': a['uuid'],
                        'res': '*',
                        'condition': condition,
                        'effect': effect,
                        'comment': '%s 对于 %s 的策略' % (role_obj.name, action_obj.name),
                        'role_based_tpl': role_obj.uuid,
                        'domain': role_obj.domain
                    }
                    self._policy_model.get_opts(create=True)
                    policy_opts = self._policy_model.validate_opts_dict(policy_fields, necessary_opts_dict)
                    print(policy_opts)
                    policy_created = self._policy_model.create_obj(**policy_opts)
                    policy_uuid_list.append(policy_created.uuid)

                # 策略绑定角色
                for p in policy_uuid_list:
                    self._m2m_model.create_obj(**{
                        'role': role_obj.uuid,
                        'policy': p
                    })

                # 更新角色
                role_fields = {
                    'tpl': role_tpl_uuid,
                    'tpl_condition_values': condition_values,
                }
                self._role_model.get_opts()
                role_opts = self._role_model.validate_opts_dict(role_fields, necessary_opts_dict)
                self._role_model.update_obj(role_obj, **role_opts)

            return self.standard_response("succeed to flush roles through tpl")

        except CustomException as e:
            return self.exception_to_response(e)