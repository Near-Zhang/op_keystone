from op_keystone.base_model import BaseModel
from django.db import models
from utils.tools import datetime_to_humanized


class Token(BaseModel):

    class Meta:
        verbose_name = 'TOKEN'
        db_table = 'token'

    # 必要字段
    user = models.CharField(max_length=32, verbose_name='用户UUID')
    token = models.CharField(max_length=32, verbose_name='TOKEN')
    expire_date = models.DateTimeField(verbose_name='过期时间')
    type = models.IntegerField(verbose_name='类型，0:access_token，2:refresh_token')

