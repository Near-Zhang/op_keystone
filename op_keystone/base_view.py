from op_keystone.exceptions import *
from django.views import View
from django.http import JsonResponse, QueryDict
from utils import tools
from utils.dao import DAO
import re


class ParamsProcessMixin:
    """
    参数处理混合类，提供提取参数的方法
    """

    @staticmethod
    def get_params_dict(request, nullable=False):
        """
        从请求中获取参数字典
        :param request: request object, 请求
        :param nullable: bool, 是否可为空
        :return: dict, 请求参数字典
        """
        # 根据方法取出数据
        if request.method == 'GET':
            request_params = request.GET
        else:
            request_params = request.body

        # 判断数据是否为空
        if not request_params:
            if not nullable:
                raise RequestParamsError(empty=True)
            else:
                request_params = {}

        # 当数据不为字典时，根据内容类型，转化数据为字典
        if not isinstance(request_params, dict):
            content_type = request.META.get('CONTENT_TYPE')
            if re.search('application/x-www-form-urlencoded', content_type):
                request_params = QueryDict(request.body)
            elif re.search('application/json', content_type):
                request_params = tools.json_loader(request_params)
                if not request_params:
                    raise RequestParamsError(not_json=True)
            else:
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
        validate = False

        for opt in opts_list:
            # 获取参数选项的 key，标记是否需要范围验证
            if type(opt) == dict:
                validate = True
                white_pass = opt.get('white')
                k = opt.get('key')
            else:
                k = opt

            # 取值后，判空以及进行范围验证
            v = request_params.get(k)
            if v is not None:
                if validate:
                    if (white_pass and v not in opt['values']) or (not white_pass and v in opt.get('values')):
                        raise RequestParamsError(opt=k, invalid=True)
                k = k.replace('-', '_')
                extract_dict[k] = v
            elif necessary:
                raise RequestParamsError(opt=opt)
        return extract_dict


class BaseView(View, ParamsProcessMixin):
    """
    基础视图类，提供返回响应的方法，以及限制非允许方法的请求
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
                try:
                    handler = getattr(self, request.method.lower())
                except AttributeError:
                    raise MethodNotAllowed(request.method.lower(), request.path)
                else:
                    return handler(request, *args, **kwargs)
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


class ResourceView(BaseView):
    """
    资源视图类，提供资源的查询和删除方法
    """

    def __init__(self, model):
        super().__init__()
        self._model = DAO(model)

    def get(self, request, uuid=None):
        try:
            # 结合请求信息，设置到 model 属性
            self._model.combine_request(request)

            # 存在 uuid 路由参数，返回单个对象
            if uuid:
                obj = self._model.get_obj(uuid=uuid)
                return self.standard_response(obj.serialize())

            # 定义参数提取列表
            extra_opts = ['query', 'query-type' , 'page', 'page-size']
            request_params = self.get_params_dict(request, nullable=True)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 查询对象生成
            query_str = extra_opts_dict.pop('query', None)
            query_type = extra_opts_dict.pop('query_type', None)
            query_obj = self._model.parsing_query_str(query_str, query_type, url_params=True)

            # 当前页数据获取
            total_list = self._model.get_dict_list(query_obj)
            page_list = tools.paging_list(total_list, **extra_opts_dict)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, uuid=None):
        try:
            # 结合请求信息，设置到 model 属性
            self._model.combine_request(request)

            # 校验创建对象权限
            self._model.validate_create()

            # 获取提取列表
            necessary_opts, extra_opts = self._model.get_opts()

            # 选项参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象字段字典参数合成，结合请求信息，校验选项参数
            field_opts = self._model.validate_opts_dict(necessary_opts_dict, extra_opts_dict)

            # 对象创建并返回
            obj = self._model.create_obj(**field_opts)
            return self.standard_response(obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, uuid=None):
        try:
            # 结合请求信息，设置到 model 属性
            self._model.combine_request(request)

            # 若 uuid 不存在，发生路由参数异常，否则获取对象，并校验对象权限
            if not uuid:
                raise RoutingParamsError()
            obj = self._model.get_obj(uuid=uuid)
            self._model.validate_obj(obj)

            # 获取提取列表
            necessary_opts, extra_opts = self._model.get_opts(create=False)

            # 选项参数提取
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 对象字段字典参数合成，结合请求信息，校验选项参数
            field_opts = self._model.validate_opts_dict(necessary_opts_dict, extra_opts_dict)

            # 对象更新并返回
            updated_obj = self._model.update_obj(obj, **field_opts)
            return self.standard_response(updated_obj.serialize())

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, uuid=None):
        try:
            # 结合请求信息，设置 model 属性
            self._model.combine_request(request)

            # 若 uuid 不存在，发生路由参数异常，否则获取对象，并校验对象权限
            if not uuid:
                raise RoutingParamsError()
            obj = self._model.get_obj(uuid=uuid)
            self._model.validate_obj(obj)

            # 对象删除并返回删除信息
            deleted_message = self._model.delete_obj(obj)
            return self.standard_response(deleted_message)

        except CustomException as e:
            return self.exception_to_response(e)


class M2MRelationView(BaseView):
    """
    多对多关系视图类，提供多对多关系的查询方法
    """

    def __init__(self, from_model, to_model, m2m_model):
        super().__init__()
        self._from_model = DAO(from_model)
        self._to_model = DAO(to_model)
        self._m2m_model = DAO(m2m_model)
        self._from_field = self._from_model.model.__name__.lower()
        self._to_field = self._to_model.model.__name__.lower()

    def get(self, request, uuid):
        try:
            # 结合请求信息，设置 model 查询参数
            self._from_model.combine_request(request)
            self._to_model.combine_request(request)

            # 保证来源对象存在
            self._from_model.get_obj(uuid=uuid)

            # 参数提取
            extra_opts = ['query', 'page', 'page-size']
            request_params = self.get_params_dict(request, nullable=True)
            extra_opts_dict = self.extract_opts(request_params, extra_opts, necessary=False)

            # 查询对象生成
            query_str = extra_opts_dict.pop('query', None)
            query_type = extra_opts_dict.pop('query_type', None)
            query_obj = self._to_model.parsing_query_str(query_str, query_type, url_params=True)

            # 获取目的对象列表，并获取当前页数据
            to_uuid_list = self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid})
            to_dict_list = self._to_model.get_dict_list(query_obj, uuid__in=to_uuid_list)
            page_list = tools.paging_list(to_dict_list, **extra_opts_dict)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def post(self, request, uuid):
        try:
            # 结合请求信息，设置 model 查询参数
            self._from_model.combine_request(request)
            self._to_model.combine_request(request)

            # 保证源对象存在，校验对象权限合法性
            from_obj = self._from_model.get_obj(uuid=uuid)
            self._from_model.validate_obj(from_obj, m2m=True)

            # 参数提取
            necessary_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 获取需要添加的目标对象 uuid 列表
            to_opts_set = set(necessary_opts_dict['uuid_list'])
            old_to_opts_set = set(self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid}))
            add_to_opts_list = list(to_opts_set - old_to_opts_set)

            # 保证每个目标对象存在，然后添加多对多关系
            for to_uuid in add_to_opts_list:
                to_obj = self._to_model.get_obj(uuid=to_uuid)
                if request.user.level != 1:
                    if self._from_field == 'role' or self._from_field == 'policy':
                        self._to_model.validate_obj(to_obj)
                        if (self._to_field == 'role' and to_obj.builtin) or \
                                (self._to_field == 'policy' and from_obj.builtin):
                            raise PermissionDenied()

                self._m2m_model.create_obj(**{
                    self._from_field: uuid,
                    self._to_field: to_uuid
                })

            # 获取最新目标对象列表，不分页获取列表所有数据
            to_uuid_list = self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid})
            to_dict_list = self._to_model.get_dict_list(uuid__in=to_uuid_list)
            page_list = tools.paging_list(to_dict_list)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def put(self, request, uuid):
        try:
            # 结合请求信息，设置 model 查询参数
            self._from_model.combine_request(request)
            self._to_model.combine_request(request)

            # 保证源对象存在，校验对象权限合法性
            from_obj = self._from_model.get_obj(uuid=uuid)
            self._from_model.validate_obj(from_obj, m2m=True)

            # 参数提取
            necessary_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 获取需要添加和删除的目标对象 uuid 列表
            to_opts_set = set(necessary_opts_dict['uuid_list'])
            old_to_opts_set = set(self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid}))
            add_to_opts_list = list(to_opts_set - old_to_opts_set)
            del_to_opts_list = list(old_to_opts_set - to_opts_set)

            # 保证每个目标对象存在，然后添加多对多关系
            for to_uuid in add_to_opts_list:
                to_obj = self._to_model.get_obj(uuid=to_uuid)
                if request.user.level != 1:
                    if self._from_field == 'role' or self._from_field == 'policy':
                        self._to_model.validate_obj(to_obj)
                        if (self._to_field == 'role' and to_obj.builtin) or \
                                (self._to_field == 'policy' and from_obj.builtin):
                            raise PermissionDenied()

                self._m2m_model.create_obj(**{
                    self._from_field: uuid,
                    self._to_field: to_uuid
                })

            # 删除多对多关系
            for to_uuid in del_to_opts_list:
                try:
                    to_obj = self._to_model.get_obj(uuid=to_uuid)
                except CustomException:
                    self._m2m_model.delete_obj_qs(**{
                        self._from_field: uuid,
                        self._to_field: to_uuid
                    })
                else:
                    if request.user.level != 1:
                        if self._from_field == 'role' or self._from_field == 'policy':
                            self._to_model.validate_obj(to_obj)
                            if (self._to_field == 'role' and to_obj.builtin) or \
                                    (self._to_field == 'policy' and from_obj.builtin):
                                raise PermissionDenied()
                    self._m2m_model.delete_obj_qs(**{
                        self._from_field: uuid,
                        self._to_field: to_uuid
                    })

            # 获取最新目标对象列表，不分页获取列表所有数据
            to_uuid_list = self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid})
            to_dict_list = self._to_model.get_dict_list(uuid__in=to_uuid_list)
            page_list = tools.paging_list(to_dict_list)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)

    def delete(self, request, uuid):
        try:
            # 结合请求信息，设置 model 查询参数
            self._from_model.combine_request(request)
            self._to_model.combine_request(request)

            # 保证源对象存在，校验对象权限合法性
            from_obj = self._from_model.get_obj(uuid=uuid)
            self._from_model.validate_obj(from_obj, m2m=True)

            # 参数提取
            necessary_opts = ['uuid_list']
            request_params = self.get_params_dict(request)
            necessary_opts_dict = self.extract_opts(request_params, necessary_opts)

            # 获取需要删除的目的对象 uuid 列表
            to_uuid_set = set(necessary_opts_dict['uuid_list'])
            old_to_uuid_set = set(self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid}))
            del_to_uuid_list = list(to_uuid_set & old_to_uuid_set)

            # 删除多对多关系
            for to_uuid in del_to_uuid_list:
                try:
                    to_obj = self._to_model.get_obj(uuid=to_uuid)
                except CustomException:
                    self._m2m_model.delete_obj_qs(**{
                        self._from_field: uuid,
                        self._to_field: to_uuid
                    })
                else:
                    if request.user.level != 1:
                        if self._from_field == 'role' or self._from_field == 'policy':
                            self._to_model.validate_obj(to_obj)
                            if (self._to_field == 'role' and to_obj.builtin) or \
                                    (self._to_field == 'policy' and from_obj.builtin):
                                raise PermissionDenied()
                    self._m2m_model.delete_obj_qs(**{
                        self._from_field: uuid,
                        self._to_field: to_uuid
                    })

            # 获取最新目标对象列表，不分页获取列表所有数据
            to_uuid_list = self._m2m_model.get_field_list(self._to_field, **{self._from_field: uuid})
            to_dict_list = self._to_model.get_dict_list(uuid__in=to_uuid_list)
            page_list = tools.paging_list(to_dict_list)

            # 返回数据
            return self.standard_response(page_list)

        except CustomException as e:
            return self.exception_to_response(e)


class MultiDeleteView(BaseView):
    """
    批量删除视图类
    """

    def __init__(self, model):
        super().__init__()
        self._model = DAO(model)

    def post(self, request):
        try:
            pass
        except CustomException as e:
            return self.exception_to_response(e)
