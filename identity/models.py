from django.db import models
from utils.tools import datetime_convert

class User(models.Model):

    class Meta:
        verbose_name = '用户'
        db_table = 'user'
        ordering = ['id']

    # 必要字段
    user_name = models.CharField(max_length=64, unique=True, verbose_name='用户名')
    real_name = models.CharField(max_length=64, verbose_name='真实姓名')
    department = models.CharField(max_length=64, verbose_name='级联部门')
    email = models.CharField(max_length=64, unique=True, verbose_name='电子邮箱')
    phone_number = models.CharField(max_length=16, verbose_name='手机号码')

    # 附加字段
    company_qq = models.CharField(max_length=16, null=True, verbose_name='企业QQ')
    enable =  models.BooleanField(default=True, verbose_name='是否可用')
    created_by = models.IntegerField(default=1, verbose_name='创建用户')
    comment = models.TextField(max_length=200, null=True, verbose_name='备注')

    # 自动生成字段
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    login_time = models.DateTimeField(null=True, verbose_name='本次登陆时间')
    last_time = models.DateTimeField(null=True, verbose_name='最近登陆时间')

    def __str__(self):
        return '{"id": %d, "username": "%s"}' %(self.id, self.user_name)

    def serialize(self):
        dict = self.__dict__
        del dict['_state']
        for i in ['created_time', 'updated_time', 'login_time', 'last_time']:
            dict[i] = datetime_convert(dict[i])
        return dict







