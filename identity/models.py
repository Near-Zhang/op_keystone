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
    deleted_time = models.DateTimeField(null=True, verbose_name='删除时间')

    def pre_create(self):
        """
        创建前，进行密码校验、字段检查
        """
        super().pre_create()
        self.validate_password()

        # 检查 domain 是否存在
        domain_obj = DAO('partition.models.Domain').get_obj(uuid=self.domain)

        # 检查 domain 中的 main user，不存在时自动创建；存在时自动不允许创建；存在多个时报错
        main_user_count = DAO('identity.models.User').get_obj_qs(domain=self.domain, is_main=True).count()
        if main_user_count < 1:
            self.is_main = True
        if main_user_count == 1 and self.is_main:
            self.is_main = False
        if main_user_count > 1:
            raise DatabaseError('more than one main user of domain %s'
                                % domain_obj.name, self.__class__.__name__)

    def post_create(self):
        """
        创建后，创建对应的 behavior 对象
        """
        DAO('identity.models.UserBehavior').create_obj(user=self.uuid)

    def pre_update(self):
        """
        更新前，进行 user 字段的检查
        """
        # 检查 domain 是否存在
        domain_obj = DAO('partition.models.Domain').get_obj(uuid=self.domain)

        # 检查 domain 中的 main user，不存在时拒绝除了新增 main user 的修改；存在时，自动禁止新增 main user 的修改，
        # 非 main domain 自动不允许禁用 main user 修改，main domain 自动不允许禁用或取消 main user 的修改；
        # 存在多个时报错
        main_user_qs = DAO('identity.models.User').get_obj_qs(domain=self.domain, is_main=True)
        main_user_count = main_user_qs.count()
        if main_user_count < 1 and not self.is_main:
                raise DatabaseError('there is no main user of domain %s'
                                    % domain_obj.name, self.__class__.__name__)
        if main_user_count == 1 :
            if self.uuid != main_user_qs.first().uuid:
                self.is_main = False
            if self.uuid == main_user_qs.first().uuid:
                self.enable = True
                if domain_obj.is_main:
                    self.is_main = True
        if main_user_count > 1:
            raise DatabaseError('more than one main user of domain %s'
                                % domain_obj.name, self.__class__.__name__)

    def pre_delete(self):
        """
        删除前，检查是否为主用户，删除对象的关联 group 和 role
        """
        if self.is_main:
            raise DatabaseError('this is the main user', self.__class__.__name__)
        DAO('identity.models.M2MUserGroup').delete_obj_qs(user=self.uuid)
        DAO('identity.models.M2MUserRole').delete_obj_qs(user=self.uuid)

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
        d['behavior'] = DAO('identity.models.UserBehavior').get_obj(user=self.uuid).serialize()
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
        进行密码合法校验，成功则进行加盐哈希，并修改到密码
        """
        try:
            v_password(self.password, self)
        except ValidationError as e:
            raise PasswordInvalid(e)
        else:
            self.password = tools.password_to_hash(self.password)

    @staticmethod
    def get_field_opts(create=True):
        """
        获取创建对象需要的字段列表
        :return:
        """
        necessary = ['username', 'password', 'name',
                     'email', 'phone']
        extra = ['qq', 'comment', 'enable']
        senior_extra = ['domain', 'is_main']

        if create:
            return necessary, extra, senior_extra
        else:
            necessary.remove('password')
            return necessary + extra, senior_extra

    @classmethod
    def get_default_query_keys(cls):
        return ['username', 'name', 'email',
                'phone', 'domain'] + super().get_default_query_keys()


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

    def pre_delete(self):
        """
        删除前，检查是否存在关联的 user，删除关联的 role
        """
        if DAO('identity.models.M2MUserGroup').get_obj_qs(group=self.uuid).count() > 0:
            raise DatabaseError('group are referenced by users', self.__class__.__name__)
        DAO('identity.models.M2MGroupRole').delete_obj_qs(group=self.uuid)

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


class M2MUserGroup(BaseModel):

    class Meta:
        verbose_name = '用户和用户组的多对多关系'
        db_table = 'm2m_user_group'
        unique_together = ('user', 'group')

    user = models.CharField(max_length=32, verbose_name='用户UUID')
    group = models.CharField(max_length=32, verbose_name='组UUID')

    def pre_create(self):
        """
        创建前，检查 user 和 group 是否同属一个 domain
        """
        user_obj = DAO(User).get_obj(uuid = self.user)
        group_obj = DAO(Group).get_obj(uuid = self.group)
        if user_obj.domain != group_obj.domain:
            raise DatabaseError('user and group is not in a common domain', self.__class__.__name__)


class M2MUserRole(BaseModel):

    class Meta:
        verbose_name = '用户和角色的多对多关系'
        db_table = 'm2m_user_role'
        unique_together = ('user', 'role')

    user = models.CharField(max_length=32, verbose_name='用户UUID')
    role = models.CharField(max_length=32, verbose_name='角色UUID')

    def pre_create(self):
        """
        创建前，检查 user 和 role 是否同属一个 domain，或者 role 是内置
        """
        user_obj = DAO(User).get_obj(uuid = self.user)
        role_obj = DAO('assignment.models.Role').get_obj(uuid = self.role)
        if user_obj.domain != role_obj.domain and not role_obj.builtin:
            raise DatabaseError('user and role is not in a common domain, and role is not builtin',
                                self.__class__.__name__)


class M2MGroupRole(BaseModel):

    class Meta:
        verbose_name = '用户组和角色的多对多关系'
        db_table = 'm2m_group_role'
        unique_together = ('group', 'role')

    group = models.CharField(max_length=32, verbose_name='用户组UUID')
    role = models.CharField(max_length=32, verbose_name='角色UUID')

    def pre_create(self):
        """
        创建前，检查 group 和 role 是否同属一个 domain，或者 role 是内置
        """
        group_obj = DAO(Group).get_obj(uuid = self.group)
        role_obj = DAO('assignment.models.Role').get_obj(uuid = self.role)
        if group_obj.domain != role_obj.domain and not role_obj.builtin:
            raise DatabaseError('group and role is not in a common domain, and role is not builtin',
                                self.__class__.__name__)
