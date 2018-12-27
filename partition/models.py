from django.db import models
from utils.tools import datetime_convert


class Project(models.Model):

    class Meta:
        verbose_name = '项目'
        db_table = 'project'
        ordering = ['id']

    # 必要字段
    project_name = models.CharField(max_length=64, unique=True, verbose_name='项目名')
    purpose = models.CharField(max_length=256, verbose_name='用途')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否可用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注')

    # 自动生成字段
    created_by = models.IntegerField(default=1, verbose_name='创建用户')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{"id": %d, "project_name": "%s"}' %(self.id, self.project_name)

    def serialize(self):
        d = self.__dict__.copy()
        del d['_state']

        for i in ['created_time', 'updated_time']:
            d[i] = datetime_convert(d[i])
        return d
