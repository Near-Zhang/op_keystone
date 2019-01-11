from op_keystone.exceptions import *
from op_keystone.baseview import BaseView
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
                domain = self.domain_model.get_object(name=domain_name)
                necessary_opts_dict['domain'] = domain.uuid

            # 取出密码
            password = necessary_opts_dict.pop('password')

            # 获取用户并校验密码
            try:
                user = self.user_model.get_object(**necessary_opts_dict)
                if user.check_password(password):

                    # 更新用户行为
                    now = tools.get_datetime_with_tz()
                    behavior_obj = self.user_behavior_model.get_object(uuid=user.uuid)
                    self.user_behavior_model.update_obj(behavior_obj, last_time=now)

                    # 生成 token 和 expire_date
                    token = tools.generate_mapping_uuid(user.domain, user.username + tools.datetime_to_humanized(now))
                    expire_date = tools.get_datetime_with_tz(minutes=settings.TOKEN_VALID_TIME)

                    # 获取用户 token 对象
                    try:
                        token_obj = self.token_model.get_object(user=user.uuid)
                    except CustomException:
                        # 不存在新建
                        self.token_model.create_obj(user=user.uuid, token=token, expire_date=expire_date)
                    else:
                        # 存在则更新
                        self.token_model.update_obj(token_obj, token=token, expire_date=expire_date)

                    # 生成浏览器 cookie 所需数据
                    data = {
                        "uuid": user.uuid,
                        "token": token,
                        "name": user.name,
                        "expire_date": tools.datetime_to_timestamp(expire_date)
                    }
                    return self.standard_response(data)

            # 登陆信息校验阶段失败，返回统一信息
            except CustomException:
                raise LoginFailed()

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
            token_ins = self.token_model.get_object(user=user.uuid)

            # 更新 token 对象
            expire_date = tools.get_datetime_with_tz()
            self.token_model.update_obj(token_ins, expire_date=expire_date)

            return self.standard_response('user %s succeed to logout' % user.name)

        except CustomException as e:
            return self.exception_to_response(e)
