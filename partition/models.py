from django.db import models
from utils.tools import (
    datetime_to_humanized, generate_unique_uuid
)


class Domain(models.Model):

    class Meta:
        verbose_name = '域'
        db_table = 'domain'

    # 逻辑生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户')

    # 必要字段
    name = models.CharField(max_length=64, unique=True, verbose_name='域名')
    company = models.CharField(max_length=64, verbose_name='公司')

    # 附加字段
    is_main = models.BooleanField(default=False, verbose_name='是否为主域')
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')

    # 自动生成字段
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{"uuid": "%s", "name": "%s"}' %(self.uuid, self.name)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ['created_time', 'updated_time']:
            d[i] = datetime_to_humanized(d[i])
        return d

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = generate_unique_uuid()


class Project(models.Model):

    class Meta:
        verbose_name = '项目'
        db_table = 'project'
        unique_together = ('domain', 'name')

    # 逻辑生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户')

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='项目名')
    domain = models.CharField(max_length=32, verbose_name='归属域')
    purpose = models.CharField(max_length=256, verbose_name='用途')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注')

    # 自动生成字段
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{"uuid": "%s", "name": "%s"}' %(self.uuid, self.name)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ['created_time', 'updated_time']:
            d[i] = datetime_to_humanized(d[i])
        return d

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成映射 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = generate_unique_uuid()