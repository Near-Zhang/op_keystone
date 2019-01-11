from op_keystone.exceptions import *
from django.views import View
from django.http.request import QueryDict
from django.http import JsonResponse
from utils.tools import json_loader


class BaseView(View):
    """
    基础视图类，提供返回响应的方法，以及限制非允许方法的请求，提取参数的方法
    """

    http_method_names = ['get', 'post', 'put', 'delete', 'options']

    @staticmethod
    def standard_response(data=None, code=200, message=None):
        """
        生成标准的 JsonResponse 对象
        :param data: dict, 数据
        :param code: int, 返回码
        :param message: str, 错误信息
        :return: JsonResponse object, json 响应对象
        """
        res_dict = {
            'code': code,
            'data': data,
            'message': message
        }
        return JsonResponse(res_dict)

    def dispatch(self, request, *args, **kwargs):
        """
        根据请求的方法，分发视图函数
        :param request: request object, 请求
        :param args: tuple, 位置参数
        :param kwargs: dict, 关键字参数
        :return: Response object, 响应对象
        """
        try:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower())
                if handler:
                    return handler(request, *args, **kwargs)
            raise MethodNotAllowed(request.method.lower(), request.path)
        except MethodNotAllowed as e:
            return self.exception_to_response(e)

    def exception_to_response(self, exception):
        """
        接收异常对象，转化为 json 响应对象并返回
        :param exception: Exception object, 异常对象
        :return: Response object, 响应对象
        """
        code = exception.code
        message = exception.__message__()
        return self.standard_response(code=code, message=message)

    @staticmethod
    def get_params_dict(request, nullable=False):
        """
        从请求中获取参数字典
        :param request: request object, 请求
        :param nullable: bool, 是否可为空
        :return: dict, 请求参数字典
        """
        if request.method == 'GET':
            request_params = request.GET
        else:
            request_params = QueryDict(request.body).get('params')

        if not request_params and not nullable:
            raise RequestParamsError(empty=True)

        if isinstance(request_params, str):
            request_params = json_loader(request_params)
            if not request_params:
                raise RequestParamsError()

        return request_params

    @staticmethod
    def extract_opts(request_params, opts_list, necessary=True):
        """
        从参数中提取指定选项，返回字典
        :param request_params: dict, 请求参数字典
        :param opts_list: list, 参数名列表
        :param necessary: bool, 是否为必要参数
        :return: dict, 提取后的参数字典
        """
        extract_dict = {}
        for opt in opts_list:
            v = request_params.get(opt)
            if v is not None:
                extract_dict[opt] = v
            elif necessary:
                raise RequestParamsError(opt=opt)
        return extract_dict