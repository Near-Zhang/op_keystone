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

    def pre_save(self):
        """
        保存前，检查是否为 main domain 的存在，和阻止创建 main domain
        :return:
        """
        main_domain_qs = self.__class__.objects.filter(is_main=True)
        if main_domain_qs.count() < 1:
            raise DatabaseError('the main domain is not existed', self.__class__.__name__)
        elif main_domain_qs.count() > 1:
            raise DatabaseError('more than one main domain', self.__class__.__name__)
        elif self.is_main and self.uuid != main_domain_qs.first().uuid:
            raise DatabaseError('the main domain is already existed ', self.__class__.__name__)

    def pre_delete(self):
        """
        删除前，检查和删除对象的对外关联
        :return:
        """
        if self.is_main:
            raise DatabaseError('this is main domain', self.__class__.__name__)


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

    def pre_save(self):
        """
        保存前，检查 domain 是否存在
        :return:
        """
        DAO('partition.models.Domain').get_obj(uuid=self.domain)
