from op_keystone.base_view import BaseView
from op_keystone.exceptions import CustomException
from utils.dao import DAO
from utils import tools


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
