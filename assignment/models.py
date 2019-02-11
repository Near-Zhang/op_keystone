from django.db import models
from utils import tools
from utils.dao import DAO


class Role(models.Model):

    class Meta:
        verbose_name = '角色'
        unique_together = ['name', 'domain']
        db_table = 'role'

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='名字')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')
    description = models.CharField(max_length=256, verbose_name='描述')

    # 附加字段
    builtin = models.BooleanField(default=False, verbose_name='是否内置')
    enable = models.BooleanField(default=True, verbose_name="是否启用")
    comment = models.CharField(max_length=64, null=True, verbose_name='备注')

    # 自动生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户UUID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户UUID')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()

    def __str__(self):
        return '{"uuid"："%s", "name": "%s"}' %(self.uuid, self.name)

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

    def pre_save(self):
        """
        保存前，检查 domain 是否存在，当角色为 builtin 时固定 domain 为 main domain
        :return:
        """
        domain_model = DAO('partition.models.Domain')
        if self.builtin:
            self.domain = domain_model.get_obj(is_main=True).uuid
        else:
            domain_model.get_obj(uuid=self.domain)


class Policy(models.Model):

    class Meta:
        verbose_name = '策略'
        db_table = 'policy'

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='名字')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')
    service = models.CharField(max_length=32, verbose_name='服务UUID')
    view = models.CharField(max_length=512, verbose_name='视图类')
    method = models.CharField(max_length=16, verbose_name='请求方法')
    request_params = models.CharField(max_length=4096, verbose_name='请求参数列表')
    view_params = models.CharField(max_length=4096, verbose_name='视图参数列表')
    effect = models.CharField(max_length=16, verbose_name='效力')

    # 附加字段
    builtin = models.BooleanField(default=False, verbose_name='是否内置')
    enable = models.BooleanField(default=True, verbose_name="是否启用")
    comment = models.CharField(max_length=64, null=True, verbose_name='备注')

    # 自动生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户UUID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户UUID')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()

    def __str__(self):
        return '{"uuid"："%s", "name": "%s"}' %(self.uuid, self.name)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ['request_params', 'view_params']:
            d[i] = tools.json_loader(d[i])

        for i in ['created_time', 'updated_time']:
            d[i] = tools.datetime_to_humanized(d[i])
        return d

    def pre_save(self):
        """
        保存前，检查 domain 是否存在，当策略为 builtin 时固定 domain 为 main domain
        :return:
        """
        domain_model = DAO('partition.models.Domain')
        if self.builtin:
            self.domain = domain_model.get_obj(is_main=True).uuid
        else:
            domain_model.get_obj(uuid=self.domain)


class M2MRolePolicy(models.Model):

    class Meta:
        verbose_name = '角色和策略的多对多关系'
        db_table = 'm2m_role_policy'
        unique_together = ('role', 'policy')

    role = models.CharField(max_length=32, verbose_name='角色UUID')
    policy = models.CharField(max_length=32, verbose_name='策略UUID')