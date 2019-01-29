from django.db import models
from op_keystone.exceptions import *
from django.contrib.auth.password_validation import validate_password as v_password
from django.core.exceptions import ValidationError


class User(models.Model):

    class Meta:
        verbose_name = '用户'
        db_table = 'user'
        unique_together = [
            ('domain', 'username', 'deleted_time'),
            ('phone', 'deleted_time'),
            ('email', 'deleted_time')
        ]

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

    # 自动生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户UUID')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='更新用户UUID')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    deleted_by = models.CharField(max_length=32, null=True, verbose_name='删除用户UUID')
    deleted_time = models.DateTimeField(null=True, verbose_name='删除时间')

    def __init__(self, *args, **kwargs):
        """
        在实例构建后创生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = tools.generate_unique_uuid()

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']
        del d['password']

        for i in ['created_time', 'updated_time', 'deleted_time']:
            if not d[i] is None:
                d[i] = tools.datetime_to_humanized(d[i])
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


class UserBehavior(models.Model):

    class Meta:
        verbose_name = '用户行为'
        db_table = 'user_behavior'

    # 逻辑生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
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

        for i in ['last_time']:
            if not d[i] is None:
                d[i] = tools.datetime_to_humanized(d[i])
        return d


class Group(models.Model):

    class Meta:
        verbose_name = '用户组'
        db_table = 'group'
        unique_together = ('domain', 'name')

    # 必要字段
    name = models.CharField(max_length=64, verbose_name='组名')
    domain = models.CharField(max_length=32, verbose_name='归属域UUID')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否可用')
    comment = models.CharField(max_length=256, null=True, verbose_name='备注')

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

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']

        for i in ['created_time', 'updated_time']:
            if not d[i] is None:
                d[i] = tools.datetime_to_humanized(d[i])
        return d


class M2MUserGroup(models.Model):

    class Meta:
        verbose_name = '用户和用户组的多对多关系'
        db_table = 'm2m_user_group'
        unique_together = ('user', 'group')

    user = models.CharField(max_length=32, verbose_name='用户UUID')
    group = models.CharField(max_length=32, verbose_name='组UUID')


class M2MUserRole(models.Model):

    class Meta:
        verbose_name = '用户和角色的多对多关系'
        db_table = 'm2m_user_role'
        unique_together = ('user', 'role')

    user = models.CharField(max_length=32, verbose_name='用户UUID')
    role = models.CharField(max_length=32, verbose_name='角色UUID')
