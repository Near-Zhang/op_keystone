from django.db import models
from utils.tools import (
    datetime_convert, password_hash, generate_unique_uuid
)


class User(models.Model):

    class Meta:
        verbose_name = '主用户'
        db_table = 'main_user'
        unique_together = ('domain', 'username')

    # 逻辑生成字段
    uuid = models.CharField(max_length=32, primary_key=True, verbose_name='UUID')
    created_by = models.CharField(max_length=32, verbose_name='创建用户')
    updated_by = models.CharField(max_length=32, null=True, verbose_name='修改用户')
    last_time = models.DateTimeField(null=True, verbose_name='最近登陆时间')

    # 必要字段
    email = models.CharField(max_length=64, unique=True, verbose_name='邮箱')
    phone = models.CharField(max_length=16, unique=True, verbose_name='手机')
    username = models.CharField(max_length=64, verbose_name='登陆名')
    domain = models.CharField(max_length=32, verbose_name='归属域')
    password = models.CharField(max_length=64, verbose_name='密码')
    name = models.CharField(max_length=64, verbose_name='用户姓名')

    # 附加字段
    is_main = models.BooleanField(default=False, verbose_name='是否为主用户')
    enable =  models.BooleanField(default=True, verbose_name='是否可用')
    qq = models.CharField(max_length=16, null=True, verbose_name='QQ')
    comment = models.CharField(max_length=200, null=True, verbose_name='备注')

    # 自动生成字段
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __init__(self, *args, **kwargs):
        """
        实例构建后生成唯一 uuid
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if not self.uuid:
            self.uuid = generate_unique_uuid()

    def __str__(self):
        return '{"uuid"："%s", "name": "%s"}' %(self.uuid, self.name)

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']
        del d['password']

        for i in ['created_time', 'updated_time', 'last_time']:
            d[i] = datetime_convert(d[i])
        return d

    def check_password(self, password):
        """
        检查密码是否正确
        :param password: str, 密码
        :return: bool
        """
        pw_hash = password_hash(password)
        if pw_hash != self.password:
            return False
        return True

