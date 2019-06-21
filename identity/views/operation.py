from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO
from django.conf import settings
from django.http.response import HttpResponse
from io import BytesIO
from django.core.cache import cache
from op_keystone.middleware import AuthTools


class LoginView(BaseView):
    """
    用户登陆，包括用户名、手机、邮箱三种登陆类型
    """

    _domain_model = DAO('partition.models.Domain')
    _user_model = DAO('identity.models.User')
    _behavior_model = DAO('identity.models.UserBehavior')
    _token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = [
                'captcha_key',
                'captcha_value',
                {
                    'key': 'type',
                    'white': True,
                    'values': ['password', 'phone']
                }
            ]
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 验证码校验
            captcha_value = necessary_opts_dict.pop('captcha_value').lower()
            captcha_value = captcha_value.lower()
            captcha_value_exp = cache.get(necessary_opts_dict.pop('captcha_key'))
            if not captcha_value_exp or captcha_value != captcha_value_exp.lower():
                raise CaptchaError()

            # 根据类型确定登陆参数，并提取
            login_type = necessary_opts_dict['type']
            if login_type == 'password':
                login_opts = ['account', 'password']
            else:
                login_opts = ['phone', 'phone_captcha']
            login_opts_dict = self.extract_opts(request_params, login_opts)

            try:
                # 密码登录, 账户参数处理并校验密码
                if login_type == 'password':
                    account = login_opts_dict['account']
                    if account.isdigit():
                        user_obj = self._user_model.get_obj(phone=account)
                    elif '@' in account:
                        try:
                            user_obj = self._user_model.get_obj(email=account)
                        except ObjectNotExist:
                            username, domain_name = account.split('@')
                            domain_uuid = self._domain_model.get_obj(name=domain_name).uuid
                            user_obj = self._user_model.get_obj(username=username, domain=domain_uuid)
                    else:
                        raise CustomException()

                    password = login_opts_dict['password']
                    user_obj.check_password(password)

                # 手机验证码登录
                else:
                    phone = login_opts_dict['phone']
                    phone_captcha = login_opts_dict['phone_captcha']
                    phone_captcha_exp = cache.get(phone)
                    if phone_captcha != phone_captcha_exp:
                        raise CustomException()
                    user_obj = self._user_model.get_obj(phone=phone)

                # 用户有效性校验
                domain_obj = self._domain_model.get_obj(uuid=user_obj.domain)
                if not user_obj.enable or not domain_obj.enable:
                    raise UserInvalid()

                # 更新用户行为
                now = tools.get_datetime_with_tz()
                remote_ip = request.META.get('REMOTE_ADDR')
                if tools.judge_private_ip(remote_ip):
                    location = '内部网络'
                else:
                    location = tools.ip_to_location(remote_ip)
                behavior_obj = self._behavior_model.get_obj(user=user_obj.uuid)
                behavior_dict = {
                    'last_type': login_type,
                    'last_time': now,
                    'last_ip': remote_ip,
                    'last_location': location
                }
                self._behavior_model.update_obj(behavior_obj, **behavior_dict)

                # 生成 access_token 和 access_expire_date
                access_mapping_str = 'access' + user_obj.username + tools.datetime_to_humanized(now)
                access_token = tools.generate_mapping_uuid(user_obj.domain, access_mapping_str)
                access_expire_date = tools.get_datetime_with_tz(minutes=settings.ACCESS_TOKEN_VALID_TIME)

                # 生成 refresh_token 和 refresh_expire_date
                refresh_mapping_str = 'token' + user_obj.username + tools.datetime_to_humanized(now)
                refresh_token = tools.generate_mapping_uuid(user_obj.domain, refresh_mapping_str)
                refresh_expire_date = tools.get_datetime_with_tz(minutes=settings.REFRESH_TOKEN_VALID_TIME)

                # 获取用户 access_token 对象，不存在新建，存在则更新
                try:
                    access_token_obj = self._token_model.get_obj(carrier=user_obj.uuid, type=0)
                except CustomException:
                    self._token_model.create_obj(carrier=user_obj.uuid, token=access_token,
                                                expire_date=access_expire_date, type=0)
                else:
                    self._token_model.update_obj(access_token_obj, token=access_token,
                                                expire_date=access_expire_date)

                # 获取用户 fresh_token 对象，不存在新建，存在则更新
                try:
                    refresh_token_obj = self._token_model.get_obj(carrier=user_obj.uuid, type=1)
                except CustomException:
                    self._token_model.create_obj(carrier=user_obj.uuid, token=refresh_token,
                                                expire_date=refresh_expire_date, type=1)
                else:
                    self._token_model.update_obj(refresh_token_obj, token=refresh_token,
                                                expire_date=refresh_expire_date)

                # 获取用户的权限级别
                domain = self._domain_model.get_obj(uuid=user_obj.domain)
                if domain.is_main:
                    if user_obj.is_main:
                        privilege_level = 1
                    else:
                        privilege_level = 2
                else:
                    privilege_level = 3

                # 生成浏览器 cookie 所需数据并返回
                data = {
                    'access_token': access_token,
                    'access_expire_date': tools.datetime_to_timestamp(access_expire_date),
                    'refresh_token': refresh_token,
                    'refresh_expire_date': tools.datetime_to_timestamp(refresh_expire_date),
                    "uuid": user_obj.uuid,
                    "name": user_obj.name,
                    "privilege_level": privilege_level
                }
                return self.standard_response(data)

            # 登陆信息校验阶段失败，返回统一信息
            except CustomException:
                raise LoginFailed()

        except CustomException as e:
            return self.exception_to_response(e)


class RefreshView(BaseView):
    """
    使用 refresh_token 刷新 access_token
    """

    token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            # refresh_token 参数提取
            necessary_opts = ['refresh_token']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 检查凭证是否过期
            rq_token = necessary_opts_dict['refresh_token']
            refresh_token_obj = self.token_model.get_obj(token=rq_token, type=1)
            now = tools.get_datetime_with_tz()
            expire_date = tools.get_datetime_with_tz(refresh_token_obj.expire_date)
            if now > expire_date:
                raise CredenceInvalid(refresh=True)

            # 刷新 refresh_token 过期时间
            refresh_expire_date = tools.get_datetime_with_tz(minutes=settings.REFRESH_TOKEN_VALID_TIME)
            self.token_model.update_obj(refresh_token_obj, expire_date=refresh_expire_date)

            # 获取 access_token，并刷新过期时间
            access_token_obj = self.token_model.get_obj(carrier=refresh_token_obj.carrier, type=0)
            access_expire_date = tools.get_datetime_with_tz(minutes=settings.ACCESS_TOKEN_VALID_TIME)
            self.token_model.update_obj(access_token_obj, expire_date=access_expire_date)

            # 返回刷新成功的新信息
            data = {
                'access_expire_date': tools.datetime_to_timestamp(access_expire_date),
                'refresh_expire_date': tools.datetime_to_timestamp(refresh_expire_date)
            }
            return self.standard_response(data)

        except CustomException as e:
            return self.exception_to_response(e)


class LogoutView(BaseView):
    """
    用户登出
    """

    _token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            # 通过用户获取 token 对象
            user = request.user
            access_token_ins = self._token_model.get_obj(carrier=user.uuid, type=0)
            refresh__token_ins = self._token_model.get_obj(carrier=user.uuid, type=1)

            # 更新 token 对象
            expire_date = tools.get_datetime_with_tz()
            self._token_model.update_obj(access_token_ins, expire_date=expire_date)
            self._token_model.update_obj(refresh__token_ins, expire_date=expire_date)

            # 返回登出成功
            return self.standard_response('user %s succeed to logout' % user.name)

        except CustomException as e:
            return self.exception_to_response(e)


class PasswordView(BaseView):
    """
    用户密码修改
    """

    user_model = DAO('identity.models.User')
    token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = ['origin_password', 'password']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 对象获取和原密码校验
            user = request.user
            origin_password = necessary_opts_dict.pop('origin_password')
            user.check_password(origin_password)

            # user 对象更新
            password = user.validate_password(necessary_opts_dict.pop('password'))
            updated_opts = {
                'password': password,
                'updated_by': request.user.uuid
            }
            self.user_model.update_obj(user, **updated_opts)

            # 获取和失效 token 对象
            user = request.user
            token_obj_qs = self.token_model.get_obj_qs(carrier=user.uuid)
            expire_date = tools.get_datetime_with_tz()
            for obj in token_obj_qs:
                self.token_model.update_obj(obj, expire_date=expire_date)

            # 返回密码修改成功
            return self.standard_response('succeed to change password')

        except CustomException as e:
            return self.exception_to_response(e)


class Captcha(BaseView):
    """
    获取生成的验证码
    """

    def get(self, request):
        try:
            # 参数提取
            necessary_opts = ['captcha-key']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 生成验证码，以及保存
            captcha_img, captcha_value = tools.generate_captcha_img(size=(95, 30))
            bytes_mem = BytesIO()
            captcha_img.save(bytes_mem, 'png')

            # 验证码信息存入缓存
            captcha_key = necessary_opts_dict['captcha_key']
            cache.set(captcha_key, captcha_value)

            # 返回图片响应
            return HttpResponse(bytes_mem.getvalue(), content_type='image/png')

        except CustomException as e:
            return self.exception_to_response(e)


class PhoneCaptcha(BaseView):
    """
    发送手机验证码
    """

    _domain_model = DAO('partition.models.Domain')
    _user_model = DAO('identity.models.User')

    def post(self, request):
        try:
            # 参数提取
            necessary_opts = [
                'captcha_key',
                'captcha_value',
                'phone'
            ]
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 验证码校验
            captcha_value = necessary_opts_dict.pop('captcha_value').lower()
            captcha_value_exp = cache.get(necessary_opts_dict.pop('captcha_key')).lower()
            if captcha_value != captcha_value_exp:
                raise CaptchaError()

            # 用户有效性校验
            user_obj = self._user_model.get_obj(**necessary_opts_dict)
            domain_obj = self._domain_model.get_obj(uuid=user_obj.domain)
            if not user_obj.enable or not domain_obj.enable:
                raise UserInvalid()

            # 发送验证码，并将验证码信息存入缓存
            expire = 60
            phone = necessary_opts_dict['phone']
            captcha_str = tools.send_phone_captcha(phone, expire=expire)
            cache.set(phone, captcha_str, timeout=expire)

            # 返回发送成功
            return self.standard_response('succeed to send captcha to %s' % phone)

        except CustomException as e:
            return self.exception_to_response(e)


class EmailCaptcha(BaseView):
    """
    发送邮箱验证码
    """

    _domain_model = DAO('partition.models.Domain')
    _user_model = DAO('identity.models.User')

    def post(self, request):
        try:
            pass

        except CustomException as e:
            return self.exception_to_response(e)


class Auth(BaseView):
    """
    用于提供接口给服务进行请求鉴权
    """

    _auth_tools = AuthTools()
    _token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            if not request.service:
                raise PermissionDenied()

            # 参数提取
            necessary_opts = ['token', 'url', 'method', 'routing_params']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 用户获取
            token_obj = self._token_model.get_obj(token=necessary_opts_dict.pop('token'))
            user_obj = self._auth_tools.get_user_of_token(token_obj)
            if user_obj.level == 1:
                return self.standard_response({
                    'access': True,
                    'allow_condition_list': [],
                    'deny_condition_list': []
                })

            # 获取 user 对象关联的 policy 列表，policy 判定处理后获取通过标记和条件
            policy_obj_qs = self._auth_tools.get_policies_of_user(user_obj)
            access, allow_condition_list, deny_condition_list = self._auth_tools.judge_policies(
                policy_obj_qs, request.service.uuid, necessary_opts_dict)

            return self.standard_response({
                'access': access,
                'allow_condition_list': allow_condition_list,
                'deny_condition_list': deny_condition_list
            })

        except CustomException as e:
            return self.exception_to_response(e)


class PrivilegeForManageActions(BaseView):
    """
    用于提供给前端关于该用户关于动作的修改权限数据，附带详细条件，用于展示按钮
    """

    _auth_tools = AuthTools()
    _token_model = DAO('credence.models.Token')
    _action_model = DAO('assignment.models.Action')
    _service_model = DAO('catalog.models.Service')

    def get(self, request):
        try:
            # 获取 user 对象关联的 policy 列表
            policy_obj_qs = self._auth_tools.get_policies_of_user(request.user)

            # 默认响应数据
            privilege_data = {
                'default_privileges': {
                    'default_service': {
                        'access': False,
                        'allow_condition_list': [],
                        'deny_condition_list': []
                    }
                },
                'privileges': {}
            }

            # 全局管理员返回拥有全部动作权限
            if request.user.level == 1:
                privilege_data['default_privileges']['default_service']['access'] = True
                return self.standard_response(privilege_data)

            # 其他用户根据生成默认权限和具体动作对应的权限数据
            for policy_obj in policy_obj_qs:
                action_obj = self._action_model.get_obj(uuid=policy_obj.action)
                action_pri = privilege_data['privileges'].get(action_obj.name)
                if not action_pri:
                    action_pri = {
                        'access': False,
                        'allow_condition_list': [],
                        'deny_condition_list': []
                    }
                service_pri = {
                    'access': False,
                    'allow_condition_list': [],
                    'deny_condition_list': []
                }

                # 全部管理权限的动作修改到 default 权限上
                res_c = None
                if policy_obj.res != '*':
                    res_c = 'uuid:' + policy_obj.res.replace(',', '|')
                if action_obj.url == '*' and action_obj.method == '*':
                    service_obj = self._service_model.get_obj(uuid=action_obj.service)
                    service_pri['access'] = True

                    if policy_obj.effect == 'allow' and policy_obj.condition:
                        service_pri['allow_condition_list'].append(policy_obj.condition)
                        if res_c:
                            service_pri['allow_condition_list'].append(res_c)

                    if policy_obj.effect == 'deny' and policy_obj.condition:
                        service_pri['deny_condition_list'].append(policy_obj.condition)
                        if res_c:
                            service_pri['deny_condition_list'].append(res_c)

                    privilege_data['default_privileges'][service_obj.name] = service_pri

                # 具体管理权限的动作修改到具体动作上，排除查询的权限
                elif action_obj.method != 'get':
                    action_pri['access'] = True
                    if policy_obj.effect == 'allow' and policy_obj.condition:
                        action_pri['allow_condition_list'].append(policy_obj.condition)
                        if res_c:
                            action_pri['allow_condition_list'].append(res_c)

                    if policy_obj.effect == 'deny' and policy_obj.condition:
                        action_pri['allow_condition_list'].append(policy_obj.condition)
                        if res_c:
                            action_pri['allow_condition_list'].append(res_c)

                    privilege_data['privileges'][action_obj.name] = action_pri

            return self.standard_response(privilege_data)

        except CustomException as e:
            return self.exception_to_response(e)


class PrivilegeForDescribeActions(BaseView):
    """
    用于提供给前端关于该用户关于动作的查看权限数据，忽略条件，用于展示菜单
    """

    _auth_tools = AuthTools()
    _token_model = DAO('credence.models.Token')
    _action_model = DAO('assignment.models.Action')
    _service_model = DAO('catalog.models.Service')

    def get(self, request):
        try:
            # 获取 user 对象关联的 policy 列表
            policy_obj_qs = self._auth_tools.get_policies_of_user(request.user)

            # 默认响应数据
            privilege_data = {
                'default_privileges': {
                    'default_service': {
                        'access': False
                    }
                },
                'privileges': {}
            }

            # 全局管理员返回拥有全部查看权限
            if request.user.level == 1:
                privilege_data['default_privileges']['default_service']['access'] = True
                return self.standard_response(privilege_data)

            # 其他用户根据生成默认权限和具体动作对应的权限数据
            for policy_obj in policy_obj_qs:
                action_obj = self._action_model.get_obj(uuid=policy_obj.action)

                action_pri = privilege_data['privileges'].get(action_obj.name)
                if not action_pri:
                    action_pri = {
                        'access': False,
                    }
                service_obj = self._service_model.get_obj(uuid=action_obj.service)
                service_pri = {
                    'access': False,
                }

                # 全部管理权限的查看修改到 default 权限上
                if action_obj.url == '*' and (action_obj.method == '*' or action_obj.method == 'get'):
                    service_pri['access'] = True
                    privilege_data['default_privileges'][service_obj.name] = service_pri

                # 具体管理权限的查看修改到具体动作上，排除修改的权限
                elif action_obj.method == 'get' or action_obj.method == '*':
                    action_pri['access'] = True
                    privilege_data['privileges'][action_obj.name] = action_pri

            return self.standard_response(privilege_data)

        except CustomException as e:
            return self.exception_to_response(e)