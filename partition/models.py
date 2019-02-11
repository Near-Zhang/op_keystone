from django.db import models
from op_keystone.exceptions import *
from utils import tools
from utils.dao import DAO


class Domain(models.Model):

    class Meta:
        verbose_name = '域'
        db_table = 'domain'

    # 必要字段
    name = models.CharField(max_length=64, unique=True, verbose_name='域名')
    company = models.CharField(max_length=64, verbose_name='公司')

    # 附加字段
    is_main = models.BooleanField(default=False, verbose_name='是否为主域')
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

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()

    def pre_save(self):
        """
        保存前，检查 main domain 是否唯一
        :return:
        """
        if self.is_main and self.__class__.objects.filter(is_main=True).count() >= 1:
            raise DatabaseError('not the single main domain', self.__class__.__name__)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ['created_time', 'updated_time']:
            d[i] = tools.datetime_to_humanized(d[i])

        # 附加信息
        d['project_count'] = Project.objects.filter(domain=self.uuid).count()
        d['user_count'] = DAO('identity.models.User').get_obj_qs(domain=self.uuid).count()
        d['group_count'] = DAO('identity.models.Group').get_obj_qs(domain=self.uuid).count()

        return d


class Project(models.Model):

    class Meta:
        verbose_name = '项目'
        db_table = 'project'
        unique_together = ('domain', 'name')

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='项目名')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')
    description = models.CharField(max_length=256, verbose_name='描述')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注')

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
        实例构建后生成映射 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()

    def pre_save(self):
        """
        保存前，检查 domain 是否存在
        :return:
        """
        DAO('partition.models.Domain').get_obj(uuid=self.domain)