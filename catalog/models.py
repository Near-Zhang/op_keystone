from django.db import models
from utils import tools


class Service(models.Model):

    class Meta:
        verbose_name = '服务'
        db_table = 'service'

    # 必要字段
    name = models.CharField(max_length=64, unique=True, verbose_name='域名')
    function = models.CharField(max_length=128, verbose_name='功能')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')

    # 自动生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户UUID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户UUID')
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
            d[i] = tools.datetime_to_humanized(d[i])
        return d

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()


class Endpoint(models.Model):
    class Meta:
        verbose_name = '端点'
        db_table = 'endpoint'
        unique_together = ('ip', 'port')

    # 必要字段
    ip = models.CharField(max_length=64, verbose_name='IP')
    port = models.CharField(max_length=8, verbose_name='端口')
    service = models.CharField(max_length=32, verbose_name='服务UUID')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')

    # 自动生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户UUID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户UUID')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{"uuid": "%s", "ip": "%s", "port": "%s"}' %(self.uuid, self.ip, self.port)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ['created_time', 'updated_time']:
            d[i] = tools.datetime_to_humanized(d[i])
        return d

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()
