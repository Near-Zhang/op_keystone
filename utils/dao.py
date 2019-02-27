from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from django.db.utils import Error
from op_keystone.exceptions import *
from utils import tools
from django.db.models import Q


class DAO:
    """
    database access object， 数据库访问对象
    """

    def __init__(self, model):
        if isinstance(model, str):
            model = tools.import_string(model)

        # 如果模型使用了软删除，则查询时添加未软删除过滤
        try:
            model._meta.get_field('deleted_time')
            self.not_soft_deleted = {
                "deleted_time__isnull": True
            }
        except FieldDoesNotExist:
            self.not_soft_deleted = {}

        self.model = model

    @staticmethod
    def parsing_query_str(query_str):
        """
        解析查询字符串为查询对象
        :param query_str: str, 查询字符串
        :return: Q object
        """
        q = Q()
        if not query_str:
            return q
        query_list = query_str.split(',')
        for sub_query in query_list:
            key = 'name__startswith'
            sub_query_list = sub_query.split(':')
            if len(sub_query_list) > 1:
                key, value_str = sub_query_list
                key += '__startswith'
            else:
                value_str = sub_query_list[0]

            value_list = value_str.split('|')
            sub_q = Q()
            for value in value_list:
                sub_q = sub_q | Q(**{key: value})

            q = q & sub_q
        return q

    def get_obj(self, **kwargs):
        """
        从模型中过滤并获取单个对象
        :param kwargs: 过滤参数
        :return: model object
        """
        try:
            return self.model.objects.get(**self.not_soft_deleted, **kwargs)
        except ObjectDoesNotExist as e:
            raise ObjectNotExist(self.model.__name__) from e

    def get_obj_qs(self, query_obj=Q(), **kwargs):
        """
        从模型中过滤并获取包含对象的查询集
        :param query_obj: Q object, 查询对象
        :param kwargs: dict, 过滤参数
        :return: query set
        """
        return self.model.objects.filter(query_obj, **self.not_soft_deleted, **kwargs)

    def get_dict_list(self, query_obj=Q(), **kwargs):
        """
        从模型中过滤并获取包含对象序列化字典的列表，用于返回响应
        :param query_obj: Q object, 查询对象
        :param kwargs: dict, 过滤参数
        :return: list, [dict, ...]
        """
        obj_qs = self.get_obj_qs(query_obj, **kwargs)
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

    def create_obj(self, check_methods=(), **kwargs):
        """
        创建一个对象到模型中
        :param check_methods: tuple, 包含多个用于自检的方法名的元祖
        :param kwargs: dict, 列参数
        :return: model object
        """
        obj = self.model(**kwargs)
        for cm in check_methods:
            getattr(obj, cm)()

        try:
            obj.save()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e
        else:
            return obj

    def update_obj(self, obj, check_methods=(), **kwargs):
        """
        从模型中修改一个对象
        :param obj: model object, 对象
        :param check_methods: tuple, 包含多个用于自检的方法名的元祖
        :param kwargs: dict, 列参数
        :return: model object
        """
        for i in kwargs:
            setattr(obj, i, kwargs[i])
        for cm in check_methods:
            getattr(obj, cm)()

        try:
            obj.save()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e
        else:
            return obj

    def delete_obj(self, obj, check_methods=(), deleted_by=None):
        """
        从模型中删除一个对象，自行区分呢是否软删除
        :param obj: model object, 对象
        :param check_methods: tuple, 包含多个用于自检的方法名的元祖
        :param deleted_by: str, 删除用户 uuid，软删除需要
        :return: model object
        """
        for cm in check_methods:
            getattr(obj, cm)()

        if hasattr(obj, 'deleted_time'):
            soft_deleted_dict = {
                'deleted_time': tools.get_datetime_with_tz(),
                'deleted_by': deleted_by
            }
            obj = self.update_obj(obj, **soft_deleted_dict)
        else:
            obj.delete()

        return obj


