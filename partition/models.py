from op_keystone.base_model import ResourceModel
from django.db import models
from op_keystone.exceptions import *
from utils.dao import DAO


class Domain(ResourceModel):

    class Meta:
        verbose_name = '域'
        db_table = 'domain'
        ordering=('-is_main',)

    # 必要字段
    name = models.CharField(max_length=64, unique=True, verbose_name='域名')
    company = models.CharField(max_length=64, verbose_name='公司')
    agent = models.CharField(max_length=64, verbose_name='代理人')

    # 附加字段
    is_main = models.BooleanField(default=False, verbose_name='是否为主域')
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')

    def pre_create(self):
        """
        创建前，检查是否为 main domain 的存在，不存在则自动创建，存在自动阻止创建，存在多个则报错
        """
        super().pre_create()

        main_domain_count = DAO('partition.models.Domain').get_obj_qs(is_main=True).count()
        if main_domain_count < 1:
            self.is_main = True
            self.enable = True
        if main_domain_count == 1:
            self.domain = False
        if main_domain_count > 1:
            raise DatabaseError('more than one main domain', self.__class__.__name__)

    def pre_update(self):
        """
        更新前，main domain 的 enable 只为 true ，检查是否 main domain 的存在
        :return:
        """
        main_domain_qs = DAO('partition.models.Domain').get_obj_qs(is_main=True)
        main_domain_count = main_domain_qs.count()
        if main_domain_count < 1:
            raise DatabaseError('there is no main domain', self.__class__.__name__)
        if main_domain_count == 1 and self.uuid == main_domain_qs.first().uuid:
            self.enable = True
        if main_domain_count > 1:
            raise DatabaseError('more than one main domain', self.__class__.__name__)

    def pre_delete(self):
        """
        删除前，检查是否为 main 对象，删除对象的对外关联
        :return:
        """
        if self.is_main:
            raise DatabaseError('this is main domain', self.__class__.__name__)
        DAO('partition.models.Project').delete_obj_qs(domain=self.uuid)
        DAO('identity.models.User').delete_obj_qs(domain=self.uuid)
        DAO('identity.models.Group').delete_obj_qs(domain=self.uuid)
        DAO('assignment.models.Role').delete_obj_qs(domain=self.uuid)
        DAO('assignment.models.Policy').delete_obj_qs(domain=self.uuid)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = super().serialize()

        # 附加信息
        d['project_count'] = Project.objects.filter(domain=self.uuid).count()
        d['user_count'] = DAO('identity.models.User').get_obj_qs(domain=self.uuid).count()
        d['group_count'] = DAO('identity.models.Group').get_obj_qs(domain=self.uuid).count()
        d['custom_role_count'] = DAO('assignment.models.Role').get_obj_qs(domain=self.uuid, builtin=False).count()
        d['custom_policy_count'] = DAO('assignment.models.Policy').get_obj_qs(domain=self.uuid, builtin=False).count()
        return d

    @staticmethod
    def get_field_opts(create=True):
        """
        获取创建对象需要的字段列表
        :return:
        """
        necessary = ['name', 'company', 'agent']
        extra = ['enable', 'comment']
        senior_extra = []

        if create:
            return necessary, extra, senior_extra
        else:
            return necessary + extra, senior_extra

    @classmethod
    def get_default_query_keys(cls):
        return ['name', 'company', 'agent'] + super().get_default_query_keys()


class Project(ResourceModel):

    class Meta:
        verbose_name = '项目'
        db_table = 'project'
        ordering = ('domain',)
        unique_together = ('domain', 'name')

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='项目名')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注')

    def pre_create(self):
        """
        创建前，检查 domain 是否存在
        """
        super().pre_create()
        DAO('partition.models.Domain').get_obj(uuid=self.domain)

    def pre_update(self):
        """
        更新前，检查 domain 是否存在
        """
        DAO('partition.models.Domain').get_obj(uuid=self.domain)

    @staticmethod
    def get_field_opts(create=True):
        """
        获取创建对象需要的字段列表
        :return:
        """
        necessary = ['name']
        extra = ['enable', 'comment']
        senior_extra = ['domain']

        if create:
            return necessary, extra, senior_extra
        else:
            return necessary + extra, senior_extra

    @classmethod
    def get_default_query_keys(cls):
        return ['name', 'domain'] + super().get_default_query_keys()
