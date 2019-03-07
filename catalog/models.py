from op_keystone.base_model import ResourceModel
from django.db import models


class Service(ResourceModel):

    class Meta:
        verbose_name = '服务'
        db_table = 'service'

    # 必要字段
    name = models.CharField(max_length=64, unique=True, verbose_name='服务名')
    function = models.CharField(max_length=128, verbose_name='功能')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')


class Endpoint(ResourceModel):

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
