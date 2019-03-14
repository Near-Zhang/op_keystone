from django.utils.deprecation import MiddlewareMixin
from django.http.response import JsonResponse
import requests
from requests.exceptions import RequestException
from django.db.models import Q


class AuthMiddleware(MiddlewareMixin):
    """
    服务鉴权中间件
    """

    _keystone_url = 'http://192.168.1.250:8888/identity/auth/'
    _auth_header = 'HTTP_X_JUNHAI_TOKEN'
    _service_token = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # 构造请求信息字典
        request_info = {
            'url': request.path,
            'method': request.method.lower(),
            'routing_params': callback_kwargs
        }

        # 获取 token
        rq_token = request.META.get(self._auth_header)
        if not rq_token:
            return JsonResponse({
                'code': 403,
                'data': None,
                'message': 'CredenceInvalid: the access token in the header is required'
            })
        request_info['token'] = rq_token

        try:
            auth_header = {
                "X-Junhai-Token": self._service_token
            }
            response = requests.post(self._keystone_url, headers=auth_header, json=request_info).json()

            if response['code'] != 200:
                return JsonResponse({
                    'code': response['code'],
                    'data': None,
                    'message': response['message']
                })

        except RequestException():
            return JsonResponse({
                'code': 502,
                'data': None,
                'message': 'RequestError: the response of post %s is not available' % self._keystone_url
            })

        # 处理鉴权响应
        if response['data']['access']:
            return JsonResponse({
                'code': 403,
                'data': None,
                'message': 'PermissionDenied: unable to access the server'
            })

        else:
            condition_q = Q()
            for condition in response['data']['deny_condition_list']:
                sub_q = self.parsing_query_str(condition)
                condition_q &= ~sub_q

            allow_q = Q()
            for condition in response['data']['allow_condition_list']:
                sub_q = self.parsing_query_str(condition)
                allow_q |= sub_q

            condition_q &= allow_q

            request.condition_q = condition_q

    @staticmethod
    def parsing_query_str(query_str):
        q = Q()
        if not query_str:
            return q

        query_list = query_str.split(',')
        for sub_query_str in query_list:
            key, value_str = sub_query_str.split(':')
            value_list = value_str.split('|')
            sub_q = Q()
            for value in value_list:
                sub_q |= Q(**{key: value})
            q &= sub_q

        return q












