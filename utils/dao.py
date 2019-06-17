from op_keystone.base_model import BaseModel, ResourceModel
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import Error
from op_keystone.exceptions import *
from utils import tools
from django.db.models import Q


class DAO:
    """
    database access object， 数据库访问对象
    """

    def __init__(self, model):
        """
        初始化 dao 对象的属性
        :param model:
        """
        if isinstance(model, str):
            model = tools.import_string(model)
        if not model or not issubclass(model, BaseModel):
            raise ValueError()

        self.model = model
        self.user = None
        self.service = None
        self.query_obj = Q()
        if self.model.get_field('deleted_time'):
            self.query_obj = Q(deleted_time__isnull=True)
        self.init_opts_dict = {}

    def combine_request(self, request):
        """
        融合请求信息，更新 dao 对象的相关属性
        :param request:  请求对象
        :return:
        """
        if hasattr(request, 'user'):
            self.user = request.user
        else:
            self.service = request.service
            return

        if getattr(request, 'condition_tuple', None):
            for condition in request.condition_tuple[1]:
                sub_q = self.parsing_query_str(condition)
                self.query_obj &= ~sub_q

            allow_q = Q()
            for condition in request.condition_tuple[0]:
                sub_q = self.parsing_query_str(condition)
                allow_q |= sub_q
            self.query_obj &= allow_q

        # 单个域级别需要设置查询限制
        if self.user.level == 3:
            if self.model.__name__ == 'Domain':
                # 对于 domain 模型，只允许查询用户所在 domain
                self.query_obj &= Q(uuid=self.user.domain)
            if self.model.get_field('domain'):
                if self.model.get_field('builtin'):
                    # 对于包含 domain、builtin 字段的模型，只允许查询用户所在 domain 以及内置的对象
                    self.query_obj &= (Q(domain=self.user.domain) | Q(builtin=True))
                else:
                    # 对于包含 domain 字段的模型，只允许查询用户所在 domain 的对象
                    self.query_obj &= Q(domain=self.user.domain)

    def validate_create(self):
        """
        融合请求的信息，校验是否有创建对象的权限
        """
        if self.service:
            return

        if not self.user:
            raise AttributeError('the attribute user is not set')

        if self.user.level != 1 and not self.model.get_field('domain'):
            if self.model.__name__ != 'Domain':
                raise PermissionDenied()
            elif self.user.level == 3:
                raise PermissionDenied()

    def validate_obj(self, obj, m2m=False):
        """
        融合请求的信息，校验对象的权限合法性，用于修改和删除对象
        :param obj: model object
        :param m2m: bool, 是否为关联性操作
        """
        if self.service:
            return

        if not self.user:
            raise AttributeError('the attribute user is not set')

        # 单个域用户级别，可以查询到自身 domain 以及所属对象、内置对象，所有无 domain 字段对象
        if self.user.level == 3:
            # 没有 domain 字段的模型，不允许操作
            if not self.model.get_field('domain'):
                raise PermissionDenied()

            # 含有 domain、builtin 字段的模型，不允许资源操作非所属用户 domain 的对象、多对多操作非所属用户且非内置对象
            elif self.model.get_field('builtin'):
                if obj.domain != self.user.domain:
                    if not m2m or (m2m and not obj.builtin):
                        raise PermissionDenied()

            # 只含有 domain 字段的模型，不允许操作非所属用户 domain 的对象
            elif obj.domain != self.user.domain:
                raise PermissionDenied()

        # 跨域用户级别，可以查询到所有对象
        if self.user.level == 2:
            # domain 模型，不允许操作主 domain
            if self.model.__name__ == 'Domain':
                if obj.uuid == self.user.domain:
                    raise PermissionDenied()

            # 没有 domain 字段的模型，不允许操作
            elif not self.model.get_field('domain'):
                raise PermissionDenied()

            # 含有 domain、builtin 字段的模型，不允许资源操作主 domain 对象、多对多操作主 domain 且非内置对象
            elif self.model.get_field('builtin'):
                if obj.domain == self.user.domain:
                    if not m2m or (m2m and not obj.builtin):
                        raise PermissionDenied()

            # 只含有 domain 字段的模型，不允许操作主 domain 的对象
            elif obj.domain == self.user.domain:
                raise PermissionDenied()

    def get_opts(self, create=True):
        """
        融合请求的信息，获取创建对象需要的选项列表
        :return:
        """
        operator = 0
        if self.user:
            operator = 1
        elif self.service:
            operator = 2

        if operator == 0:
            raise AttributeError('the attribute user is not set')
        if not issubclass(self.model, ResourceModel):
            raise ValueError('the model is not a subclass of ResourceModel')

        if create:
            # 初始选项字典设置
            if operator == 1:
                self.init_opts_dict['created_by'] = self.user.uuid
                if self.model.get_field('domain'):
                    self.init_opts_dict['domain'] = self.user.domain

            # 选项列表获取
            necessary, extra, senior_extra = getattr(self.model, 'get_field_opts')()

            if operator == 2:
                necessary += ['created_by', 'domain']
                return necessary, extra + senior_extra

            if self.user.level == 3:
                return necessary, extra
            else:
                return necessary, extra + senior_extra
        else:
            # 初始选项字典设置
            if operator == 1:
                self.init_opts_dict['updated_by'] = self.user.uuid

            # 选项列表获取
            extra, senior_extra = getattr(self.model, 'get_field_opts')(create=False)
            necessary = []

            if operator == 2:
                necessary = ['updated_by']
                return necessary, extra + senior_extra

            if self.user.level == 3:
                return necessary, extra
            else:
                return necessary, extra + senior_extra

    def validate_opts_dict(self, *opts_dicts):
        """
        融合请求的信息，校验选项字典的权限合法性，新增对象使用
        :param opts_dicts: 选项字典
        :return: dict, 字段参数字典
        """
        if self.service:
            return opts_dicts

        if not self.init_opts_dict:
            raise AttributeError('the attribute init_opts_dict is not set')

        # 完整对象字段字典参数合成
        field_opts = {}
        field_opts.update(self.init_opts_dict)
        for opts_dict in opts_dicts:
            field_opts.update(opts_dict)

        # 校验字段字典
        if not self.model.get_field('domain'):
            if self.user.level == 3:
                raise PermissionDenied()

        if self.user.level == 2:
            # 跨域级别不允许操作包含 domain 字段的模型的主 domain 的对象
            if self.model.get_field('domain') and field_opts['domain'] == self.user.domain:
                raise PermissionDenied()
            # 跨域级别不允许操作包含 builtin 字段的模型的主 builtin 的对象
            if self.model.get_field('builtin') and field_opts['builtin']:
                raise PermissionDenied()

        return field_opts

    def parsing_query_str(self, query_str, query_type='startswith', url_params=False):
        """
        解析查询字符串为查询对象
        :param query_str: str, 查询字符串
        :param query_type: str, 查询类型
        :param url_params: bool, 是否由 url 参数传递
        :return: Q object
        """
        q = Q()
        if not query_str:
            return q

        query_type_list = [
            'exact', 'iexact', 'contains',
            'icontains', 'startswith', 'istartswith',
            'endswith', 'iendswith '
        ]
        if query_type not in query_type_list:
            query_type = 'startswith'

        query_list = query_str.split(',')
        for sub_query_str in query_list:
            if ':' not in sub_query_str:
                if url_params:
                    sub_q = Q()
                    for key in getattr(self.model, 'get_default_query_keys')():
                        value_list = sub_query_str.split('|')
                        inside_q = Q()
                        if url_params:
                            key = key + '__' + query_type
                        for value in value_list:
                            inside_q |= Q(**{key: value})
                        sub_q |= inside_q
                else:
                    continue
            else:
                key, value_str = sub_query_str.split(':')
                get_custom_query_keys = getattr(self.model, 'get_custom_query_keys', None)
                if get_custom_query_keys and key in get_custom_query_keys():
                    sub_q = getattr(self.model, 'parsing_custom_query')(key, value_str)
                elif ('__' in key and not self.model.get_field(key.split('__')[0])) or \
                    ('__' not in key and not self.model.get_field(key)):
                    continue
                else:
                    value_list = value_str.split('|')
                    sub_q = Q()
                    if url_params:
                        key = key + '__' + query_type
                    for value in value_list:
                        sub_q |= Q(**{key: value})
            q &= sub_q
        return q

    def get_obj(self, *query_obj, **kwargs):
        """
        从模型中过滤并获取单个对象
        :param query_obj: Q object, 查询对象
        :param kwargs: 过滤参数
        :return: model object
        """
        try:
            return self.model.objects.get(*query_obj, self.query_obj, **kwargs)
        except ObjectDoesNotExist as e:
            raise ObjectNotExist(self.model.__name__) from e

    def get_obj_qs(self, *query_obj, **kwargs):
        """
        从模型中过滤并获取包含对象的查询集
        :param query_obj: Q object, 查询对象
        :param kwargs: dict, 过滤参数
        :return: query set
        """
        return self.model.objects.filter(*query_obj, self.query_obj, **kwargs)

    def get_dict_list(self, *query_obj, **kwargs):
        """
        从模型中过滤并获取包含对象序列化字典的列表，用于返回响应
        :param query_obj: Q object, 查询对象
        :param kwargs: dict, 过滤参数
        :return: list, [dict, ...]
        """
        obj_qs = self.get_obj_qs(*query_obj, **kwargs)
        dict_list = []
        for obj in obj_qs:
            dict_list.append(obj.serialize())
        return dict_list

    def get_field_list(self, field, **kwargs):
        """
        从模型中过滤并获取包含对象指定列的序列化字典的列表
        :param field: str, 列名
        :param kwargs: dict, 过滤参数
        :return: list, [str,...]
        """
        obj_qs = self.get_obj_qs(**kwargs)
        field_list = []
        for obj in obj_qs:
            field_list.append(getattr(obj, field))
        return field_list

    def create_obj(self, **field_opts):
        """
        在模型中创建一个对象
        :param field_opts: dict, 列参数
        :return: model object
        """
        obj = self.model(**field_opts)
        obj.pre_create()

        try:
            obj.save()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e

        obj.post_create()
        return obj

    def update_obj(self, obj, **field_opts):
        """
        从模型中修改一个指定对象
        :param obj: model object, 对象
        :param field_opts: dict, 字段参数
        :return: model object
        """
        for i in field_opts:
            setattr(obj, i, field_opts[i])
        obj.pre_update()

        try:
            obj.save()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e

        obj.post_update()
        return obj

    def delete_obj(self, obj):
        """
        从模型中删除一个指定对象，自动区分并进行软删除
        :param obj: model object, 对象
        :return: str, 成功删除信息
        """
        obj.pre_delete()

        try:
            if hasattr(obj, 'deleted_time'):
                obj.deleted_time = tools.get_datetime_with_tz()
                obj.save()
            else:
                obj.delete()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e

        obj.post_delete()
        return 'success to delete object'

    def delete_obj_qs(self, *query_obj, **kwargs):
        """
        从模型中删除符合条件的所有对象，自动区分并进行软删除
        :param query_obj: Q object, 查询对象
        :param kwargs: dict, 过滤参数
        :return: str, 成功删除信息
        """
        obj_qs = self.get_obj_qs(*query_obj, **kwargs)

        for obj in obj_qs:
            self.delete_obj(obj)

        return 'success to delete object query set'



