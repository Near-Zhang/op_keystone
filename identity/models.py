from op_keystone.base_model import BaseModel, ResourceModel
from django.db import models
from op_keystone.exceptions import *
from django.contrib.auth.password_validation import validate_password as v_password
from django.core.exceptions import ValidationError
from utils.dao import DAO
from utils import tools


class User(ResourceModel):

    class Meta:
        verbose_name = '用户'
        db_table = 'user'
        unique_together = [
            ('domain', 'name', 'deleted_time'),
            ('domain', 'username', 'deleted_time'),
            ('phone', 'deleted_time'),
            ('email', 'deleted_time')
        ]
        ordering = ('-domain', '-is_main')

    # 必要字段
    email = models.CharField(max_length=64, verbose_name='邮箱')
    phone = models.CharField(max_length=16, verbose_name='手机')
    username = models.CharField(max_length=64, verbose_name='登陆名')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')
    password = models.CharField(max_length=64, verbose_name='密码')
    name = models.CharField(max_length=64, verbose_name='用户姓名')

    # 附加字段
    is_main = models.BooleanField(default=False, verbose_name='是否主用户')
    enable = models.BooleanField(default=True, verbose_name='是否可用')
    qq = models.CharField(max_length=16, null=True, verbose_name='QQ')
    comment = models.CharField(max_length=256, null=True, verbose_name='备注')

    # 软删除字段
    deleted_by = models.CharField(max_length=32, null=True, verbose_name='删除用户UUID')
    deleted_time = models.DateTimeField(null=True, verbose_name='删除时间')

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = super().serialize()
        del d['password']

        if not d['deleted_time'] is None:
            d['deleted_time'] = tools.datetime_to_humanized(d['deleted_time'])

        # 附加信息
        d['behavior'] = UserBehavior.objects.get(user=self.uuid).serialize()
        return d

    def check_password(self, password):
        """
        检查密码是否正确
        :param password: str, 密码
        :return: bool
        """
        pw_hash = tools.password_to_hash(password)
        if pw_hash != self.password:
            raise PasswordError

    def validate_password(self):
        """
        进行密码合法校验，成功则进行加盐哈希并返回 True
        :return: bool
        """
        try:
            v_password(self.password, self)
        except ValidationError as e:
            raise PasswordInvalid(e)
        else:
            self.password = tools.password_to_hash(self.password)

    def pre_save(self):
        """
        保存前，检查 domain 是否存在，且其中 main user 是否唯一
        """
        domain_obj = DAO('partition.models.Domain').get_obj(uuid=self.domain)
        main_user_qs = self.__class__.objects.filter(domain=self.domain, is_main=True)

        if main_user_qs.count() < 1:
            if not self.is_main:
                raise DatabaseError('main user of domain %s is not existed' % domain_obj.name, self.__class__.__name__)
        elif main_user_qs.count() > 1:
            raise DatabaseError('more than one main user of domain %s' % domain_obj.name, self.__class__.__name__)
        elif self.is_main and self.uuid != main_user_qs.first().uuid:
            raise DatabaseError('main user of domain %s is already existed' % domain_obj.name, self.__class__.__name__)
        elif domain_obj.is_main and not self.is_main and self.uuid == main_user_qs.first().uuid:
            raise DatabaseError('this is main user of domain %s' % domain_obj.name, self.__class__.__name__)

    def pre_delete(self):
        """
        删除前，检查是否为主用户，删除对象的对外关联
        """
        if self.is_main:
            raise DatabaseError('this is the main user', self.__class__.__name__)
        M2MUserGroup.objects.filter(user=self.uuid).delete()
        M2MUserRole.objects.filter(user=self.uuid).delete()


class UserBehavior(BaseModel):

    class Meta:
        verbose_name = '用户行为'
        db_table = 'user_behavior'

    # 逻辑生成字段
    user = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    last_time = models.DateTimeField(null=True, verbose_name='上次登陆时间')
    last_ip = models.CharField(max_length=16, null=True, verbose_name='上次登陆IP')
    last_location = models.CharField(max_length=32, null=True, verbose_name='上次登陆地址')

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']
        del d['user']

        if not d['last_time'] is None:
            d['last_time'] = tools.datetime_to_humanized(d['last_time'])
        return d


class Group(ResourceModel):

    class Meta:
        verbose_name = '用户组'
        db_table = 'group'
        unique_together = ('domain', 'name')
        ordering = ('-domain',)

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='组名')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否可用')
    comment = models.CharField(max_length=256, null=True, verbose_name='备注')

    def pre_save(self):
        """
        保存前，检查 domain 是否存在
        :return:
        """
        DAO('partition.models.Domain').get_obj(uuid=self.domain)

    def pre_delete(self):
        """
        删除前，检查和删除对象的对外关联
        :return:
        """
        if M2MUserGroup.objects.filter(group=self.uuid).count() > 0:
            raise DatabaseError('group are referenced by users', self.__class__.__name__)
        M2MGroupRole.objects.filter(group=self.uuid).delete()


class M2MUserGroup(BaseModel):

    class Meta:
        verbose_name = '用户和用户组的多对多关系'
        db_table = 'm2m_user_group'
        unique_together = ('user', 'group')

    user = models.CharField(max_length=32, verbose_name='用户UUID')
    group = models.CharField(max_length=32, verbose_name='组UUID')


class M2MUserRole(BaseModel):

    class Meta:
        verbose_name = '用户和角色的多对多关系'
        db_table = 'm2m_user_role'
        unique_together = ('user', 'role')

    user = models.CharField(max_length=32, verbose_name='用户UUID')
    role = models.CharField(max_length=32, verbose_name='角色UUID')


class M2MGroupRole(BaseModel):

    class Meta:
        verbose_name = '用户组和角色的多对多关系'
        db_table = 'm2m_group_role'
        unique_together = ('group', 'role')

    group = models.CharField(max_length=32, verbose_name='用户组UUID')
    role = models.CharField(max_length=32, verbose_name='角色UUID')