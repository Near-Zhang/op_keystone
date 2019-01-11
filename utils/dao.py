from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import Error
from op_keystone.exceptions import *
from utils import tools


class DAO:
    """
    database access object， 数据库访问对象
    """

    def __init__(self, model):
        if isinstance(model, str):
            model = tools.import_string(model)
        self.model = model

    def get_object(self, **kwargs):
        """
        从模型中获取单个对象
        :param kwargs: 过滤参数
        :return: model object
        """
        try:
            return self.model.objects.get(**kwargs)
        except ObjectDoesNotExist as e:
            raise ObjectNotExist(self.model.__name__) from e

    def get_obj_qs(self, **kwargs):
        """
        从模型中获取包含对象的查询集
        :param kwargs: dict, 过滤参数
        :return: query set
        """
        return self.model.objects.filter(**kwargs)

    def get_dict_list(self, **kwargs):
        """
        从模型中获取包含对象序列化成的字典的列表，用于返回响应
        :param kwargs: dict, 过滤参数
        :return: list, [dict, ...]
        """
        obj_qs = self.get_obj_qs(**kwargs)
        dict_list = []
        for obj in obj_qs:
            dict_list.append(obj.serialize())
        return dict_list

    def create_obj(self, **kwargs):
        """
        创建一个对象到模型中
        :param kwargs: dict, 列参数
        :return: model object
        """
        try:
            obj = self.model(**kwargs)
            obj.save()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e
        return obj

    def update_obj(self, obj, **kwargs):
        """
        从模型中修改一个对象
        :param obj: model object, 对象
        :param kwargs: dict, 列参数
        :return: model object
        """
        for i in kwargs:
            setattr(obj, i, kwargs[i])
        try:
            obj.save()
        except Error as e:
            msg = e.args[1]
            raise DatabaseError(msg, self.model.__name__) from e
        return obj

    @staticmethod
    def delete_obj(obj):
        """
        从模型中删除一个对象
        :param obj: model object, 对象
        :return: model object
        """
        obj.delete()
        return obj
