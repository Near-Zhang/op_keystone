from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO
from django.conf import settings


class LoginView(BaseView):
    """
    用户登陆，包括用户名、手机、邮箱三种登陆类型
    """

    domain_model = DAO('partition.models.Domain')
    user_model = DAO('identity.models.User')
    user_behavior_model = DAO('identity.models.UserBehavior')
    token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            # 类型参数提取
            type_opts = ['type']
            request_params = self.get_params_dict(request)
            type_opts_dict = self.extract_opts(request_params, type_opts)

            # 根据类型确定登陆参数
            login_type = type_opts_dict['type']
            if login_type == 'phone':
                necessary_opts = ['phone', 'password']
            elif login_type == 'email':
                necessary_opts = ['email', 'password']
            else:
                necessary_opts = ['domain', 'username', 'password']

            # 登陆参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # domain 参数额外处理
            if necessary_opts_dict.get('domain'):
                domain_name = necessary_opts_dict.pop('domain')
                domain = self.domain_model.get_obj(name=domain_name)
                necessary_opts_dict['domain'] = domain.uuid

            # 取出密码
            password = necessary_opts_dict.pop('password')

            # 获取用户并校验密码，然后进行登陆成功的后续操作
            try:
                user = self.user_model.get_obj(**necessary_opts_dict)
                user.check_password(password)

                # 更新用户行为
                now = tools.get_datetime_with_tz()
                remote_ip = request.META.get('REMOTE_ADDR')
                location = tools.ip_to_location(remote_ip)
                behavior_obj = self.user_behavior_model.get_obj(user=user.uuid)
                behavior_dict = {
                    'last_time': now,
                    'last_ip': remote_ip,
                    'last_location': location
                }
                self.user_behavior_model.update_obj(behavior_obj, **behavior_dict)

                # 生成 access_token 和 access_expire_date
                access_mapping_str = 'access' + user.username + tools.datetime_to_humanized(now)
                access_token = tools.generate_mapping_uuid(user.domain, access_mapping_str)
                access_expire_date = tools.get_datetime_with_tz(minutes=settings.ACCESS_TOKEN_VALID_TIME)

                # 生成 refresh_token 和 refresh_expire_date
                refresh_mapping_str = 'token' + user.username + tools.datetime_to_humanized(now)
                refresh_token = tools.generate_mapping_uuid(user.domain, refresh_mapping_str)
                refresh_expire_date = tools.get_datetime_with_tz(minutes=settings.REFRESH_TOKEN_VALID_TIME)

                # 获取用户 access_token 对象，不存在新建，存在则更新
                try:
                    access_token_obj = self.token_model.get_obj(user=user.uuid, type=0)
                except CustomException:
                    self.token_model.create_obj(user=user.uuid, token=access_token,
                                                expire_date=access_expire_date, type=0)
                else:
                    self.token_model.update_obj(access_token_obj, token=access_token,
                                                expire_date=access_expire_date)

                # 获取用户 fresh_token 对象，不存在新建，存在则更新
                try:
                    refresh_token_obj = self.token_model.get_obj(user=user.uuid, type=1)
                except CustomException:
                    self.token_model.create_obj(user=user.uuid, token=refresh_token,
                                                expire_date=refresh_expire_date, type=1)
                else:
                    self.token_model.update_obj(refresh_token_obj, token=refresh_token,
                                                expire_date=refresh_expire_date)

                # 生成浏览器 cookie 所需数据
                data = {
                    'access_token': access_token,
                    'access_expire_date': tools.datetime_to_timestamp(access_expire_date),
                    'refresh_token': refresh_token,
                    'refresh_expire_date': tools.datetime_to_timestamp(refresh_expire_date),
                    "uuid": user.uuid,
                    "domain": user.domain,
                    "name": user.name,
                }
                return self.standard_response(data)

            # 登陆信息校验阶段失败，返回统一信息
            except CustomException as e:
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
            access_token_obj = self.token_model.get_obj(user=refresh_token_obj.user, type=0)
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

    token_model = DAO('credence.models.Token')

    def post(self, request):
        try:
            # 通过用户获取 token 对象
            user = request.user
            access_token_ins = self.token_model.get_obj(user=user.uuid, type=0)
            refresh__token_ins = self.token_model.get_obj(user=user.uuid, type=1)

            # 更新 token 对象
            expire_date = tools.get_datetime_with_tz()
            self.token_model.update_obj(access_token_ins, expire_date=expire_date)
            self.token_model.update_obj(refresh__token_ins, expire_date=expire_date)

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
            necessary_opts_dict['updated_by'] = request.user.uuid
            check_methods = ('validate_password',)
            self.user_model.update_obj(user, check_methods=check_methods, **necessary_opts_dict)

            # 获取和更新 token 对象
            user = request.user
            token_ins = self.token_model.get_obj(user=user.uuid)
            expire_date = tools.get_datetime_with_tz()
            self.token_model.update_obj(token_ins, expire_date=expire_date)

            return self.standard_response('succeed to change password')

        except CustomException as e:
            return self.exception_to_response(e)
