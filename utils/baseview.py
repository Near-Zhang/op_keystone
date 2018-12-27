from django.views import View
from django.http import JsonResponse
from utils.tools import json_loader


class BaseView(View):
    """
    基础视图
    """
    def base_json_response(self, data=None, code=200, message=None):
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

    def extract_opts(self, request_opts, necessary_opts_list, additional_opts_list):
        """
        从请求参数字典或 json 中提取出必要参数和可选参数，若必要参数缺失返回错误 JsonResponse 对象
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
