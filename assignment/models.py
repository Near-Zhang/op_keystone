from op_keystone.base_model import BaseModel, ResourceModel
from django.db import models
from utils.dao import DAO
from op_keystone.exceptions import DatabaseError


class Role(ResourceModel):

    class Meta:
        verbose_name = '角色'
        unique_together = ['name', 'domain']
        db_table = 'role'
        ordering = ('-builtin',)

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='名字')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')

    # 附加字段
    builtin = models.BooleanField(default=False, verbose_name='是否内置')
    enable = models.BooleanField(default=True, verbose_name="是否启用")
    comment = models.CharField(max_length=64, null=True, verbose_name='备注')

    def pre_create(self):
        """
        创建前，检查 domain 是否存在，以及是否内置
        """
        super().pre_create()

        if self.builtin:
            self.domain = DAO('partition.models.Domain').get_obj(is_main=True).uuid
        else:
            DAO('partition.models.Domain').get_obj(uuid=self.domain)

    @staticmethod
    def get_field_opts(create=True):
        """
        获取创建对象需要的字段列表
        :return:
        """
        necessary = ['name']
        extra = ['comment', 'enable']
        senior_extra = ['domain', 'builtin']

        if create:
            return necessary, extra, senior_extra
        else:
            return necessary + extra, senior_extra

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

    def pre_delete(self):
        """
        删除前，检查对象的对外关联
        :return:
        """
        if DAO('identity.models.M2MUserRole').get_obj_qs(role=self.uuid).count() > 0:
            raise DatabaseError('role are referenced by users', self.__class__.__name__)
        if DAO('identity.models.M2MGroupRole').get_obj_qs(role=self.uuid).count() > 0:
            raise DatabaseError('role are referenced by groups', self.__class__.__name__)
        M2MRolePolicy.objects.filter(role=self.uuid).delete()


class Policy(ResourceModel):

    class Meta:
        verbose_name = '策略'
        unique_together = ['name', 'domain']
        db_table = 'policy'
        ordering = ('-builtin',)

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='名字')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')
    action = models.CharField(max_length=64, verbose_name='动作UUID')
    res = models.TextField(verbose_name='资源列表')
    condition = models.CharField(max_length=512, null=True, verbose_name='资源条件')
    effect = models.CharField(max_length=16, verbose_name='效力')

    # 附加字段
    builtin = models.BooleanField(default=False, verbose_name='是否内置')
    enable = models.BooleanField(default=True, verbose_name="是否启用")
    comment = models.CharField(max_length=64, null=True, verbose_name='备注')

    def pre_save(self):
        """
        保存前，检查 domain、service 是否存在，当策略为 builtin 时固定 domain 为 main domain
        :return:
        """
        DAO('assignment.models.Action').get_obj(uuid=self.action)
        domain_model = DAO('partition.models.Domain')
        if self.builtin:
            self.domain = domain_model.get_obj(is_main=True).uuid
        else:
            domain_model.get_obj(uuid=self.domain)

    def pre_delete(self):
        """
        删除前，检查对象的对外关联
        :return:
        """
        if M2MRolePolicy.objects.filter(policy=self.uuid).count() > 0:
            raise DatabaseError('policy are referenced by roles', self.__class__.__name__)


class Action(ResourceModel):

    class Meta:
        verbose_name = '动作'
        unique_together = ['name', 'service']
        db_table = 'action'

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='名字')
    service = models.CharField(max_length=32, verbose_name='服务UUID')
    url = models.CharField(max_length=512, verbose_name='url正则')
    method = models.CharField(max_length=16, verbose_name='请求方法')

    # 附加字段
    comment = models.CharField(max_length=64, null=True, verbose_name='备注')

    def pre_save(self):
        """
        保存前，检查 service 是否存在
        :return:
        """
        DAO('catalog.models.Service').get_obj(uuid=self.service)

    def pre_delete(self):
        """
        删除前，检查对象的对外关联
        :return:
        """
        if Policy.objects.filter(action=self.uuid).count() > 0:
            raise DatabaseError('action are referenced by policies', self.__class__.__name__)


class M2MRolePolicy(BaseModel):

    class Meta:
        verbose_name = '角色和策略的多对多关系'
        db_table = 'm2m_role_policy'
        unique_together = ('role', 'policy')

    role = models.CharField(max_length=32, verbose_name='角色UUID')
    policy = models.CharField(max_length=32, verbose_name='策略UUID')