from django.http import JsonResponse
from django.shortcuts import redirect
from utils.tools import (
    json_loader, get_datetime_with_tz
)
from django.conf import settings
from credence.models import Token
from identity.models import User
from utils import dao


class BaseViewMixin:
    """
    基础视图混合类，提供常用的方法和请求返回
    """
    @staticmethod
    def base_json_response(data=None, code=200, message=None):
        """
        简便生成 JsonResponse object
        :param data: dict, 数据
        :param code: int, 返回码
        :param message: str, 错误信息
        :return: JsonResponse object
        """
        if code != 200 and not message:
            dict = {
                'code': 500,
                'data': data,
                'message': 'InternalError:response is not compelete'
            }
        else:
            dict = {
                'code': code,
                'data': data,
                'message': message
            }
        return JsonResponse(dict)

    def extract_opts_or_400(self, request_opts, necessary_opts_list, additional_opts_list):
        """
        从请求参数字典或 json 中提取出必要参数和可选参数，若必要参数缺失返回 400 JsonResponse 对象
        :param request_opts: dict or str, 请求参数
        :param necessary_opts_list: list, 必要参数列表
        :param additional_opts_list: list, 可选参数列表
        :return: tuple, (response, necessary_opts_dict, additional_opts_dict)
        """
        if not request_opts:
            message = 'ParamsError:params is none'
            return self.base_json_response(code=400, message=message), None, None

        if isinstance(request_opts ,str):
            request_opts = json_loader(request_opts)
            if not request_opts:
                message = 'ParamsError:params is not a standard json'
                return self.base_json_response(code=400, message=message), None, None

        necessary_opts_dict = {}
        for k in necessary_opts_list:
            v = request_opts.get(k)
            if v is not None:
                necessary_opts_dict[k] = v
            else:
                message = 'ParamsError:param %s is missing or none' %k
                return self.base_json_response(code=400, message=message), None, None

        additional_opts_dict = {}
        for k in additional_opts_list:
            v = request_opts.get(k)
            if v is not None:
                additional_opts_dict[k] = v

        return None, necessary_opts_dict, additional_opts_dict

    def get_object_or_404(self, model, **kwargs):
        """
        获取对象，不存在返回 404 JsonResponse 对象
        :param model: Model, 模型
        :param kwargs: dict, 筛选条件
        :return: tuple, (respond, obj)
        """
        obj = dao.get_object_from_model(model, **kwargs)
        if not obj:
            message = 'ObjectDoesNotExist:failed to find object of %s' % model.__name__
            return self.base_json_response(code=404, message=message), None
        return None, obj

    def get(self, request):
        message = 'MethodError: %s is not supported by get method' %request.path
        return self.base_json_response(code=403, message=message)

    def post(self, request):
        message = 'MethodError: %s is not supported by post method' %request.path
        return self.base_json_response(code=403, message=message)

    def put(self, request):
        message = 'MethodError: %s is not supported by put method' %request.path
        return self.base_json_response(code=403, message=message)

    def delete(self, request):
        message = 'MethodError: %s is not supported by delete method' %request.path
        return self.base_json_response(code=403, message=message)


class LoginRequireMixin(BaseViewMixin):
    """
    要求登陆视图混合类，覆写 dispatch 方法
    """
    def set_user_attr(self, request, uuid):
        respond, user = self.get_object_or_404(User, uuid=uuid)
        if user:
            request.user = user
            return True
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        rq_uuid = request.COOKIES.get('uuid')
        rq_token = request.COOKIES.get('token')
        if rq_uuid and rq_token:
            now = get_datetime_with_tz()
            respond, token = self.get_object_or_404(Token, user=rq_uuid, token=rq_token)
            if token:
                expire_date = get_datetime_with_tz(token.expire_date)
                if now <= expire_date:
                    if self.set_user_attr(request, rq_uuid):
                        return super().dispatch(request, *args, **kwargs)
        return redirect(settings.LOGIN_URL)