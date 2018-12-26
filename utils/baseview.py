from django.views import View
from django.http import JsonResponse


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

    def get_necessary_opts(self, request_opts, opts_list):
        """
        判断请求参数是否包含必要参数，如包含返回必要参数字典
        :param request_opts: dict, 请求参数字典
        :param opts_list: list, 必要参数列表
        :return: tuple, (True, dict) or (False, JsonResponse object)，dict 为必要参数字典
        """
        opts_dict = {}
        for k in opts_list:
            v = request_opts.get(k)
            if v:
                opts_dict[k] = v
            else:
                message = 'ParamsError:missing params'
                return False, self.base_json_response(code=400, message=message)
        return True, opts_dict

    def get_additional_opts(self, request_opts, opts_list):
        """
        返回请求参数中的附加参数字典
        :param request_opts: dict, 请求参数字典
        :param opts_list: list, 附加参数列表
        :return: dict, 附加参数字典
        """
        opts_dict = {}
        for k in opts_list:
            v = request_opts.get(k)
            if v:
                opts_dict[k] = v
        return opts_dict

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
