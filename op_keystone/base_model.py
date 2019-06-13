from django.db import models
from utils import tools
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q


class BaseModel(models.Model):

    class Meta:
        verbose_name = '基础抽象模型'
        abstract = True

    def pre_create(self):
        """
        创建前的检查和操作
        """
        pass

    def post_create(self):
        """
        创建后的检查和操作
        """
        pass

    def pre_update(self):
        """
        更新前的检查和操作
        """
        pass

    def post_update(self):
        """
        更新后的检查和操作
        """
        pass

    def pre_delete(self):
        """
         删除前的检查和操作
        """
        pass

    def post_delete(self):
        """
         删除后的检查和操作
        """
        pass

    @classmethod
    def get_field(cls, field_name):
        """
        从 model 中获取指定 field 对象
        :param field_name: str, 字段名
        :return: field object
        """
        try:
            field_obj = getattr(cls, '_meta').get_field(field_name)
            return field_obj
        except FieldDoesNotExist:
            return


class ResourceModel(BaseModel):

    class Meta:
        verbose_name = '资源抽象模型'
        abstract = True

    # 共有字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户UUID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户UUID')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def pre_create(self):
        """
        创建前的检查和操作，创建 uuid
        """
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ('created_time', 'updated_time'):
            if not d[i] is None:
                d[i] = tools.datetime_to_humanized(d[i])
        return d

    @classmethod
    def get_default_query_keys(cls):
        return ['uuid']

    @classmethod
    def get_custom_query_keys(cls):
        return []

    @classmethod
    def parsing_custom_query(cls, key, value):
        return Q()
