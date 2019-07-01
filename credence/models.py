from op_keystone.base_model import BaseModel
from django.db import models


class Token(BaseModel):

    class Meta:
        verbose_name = 'TOKEN'
        db_table = 'token'
        unique_together = ('carrier', 'type')

    # 必要字段
    carrier = models.CharField(max_length=32, verbose_name='载体UUID')
    token = models.CharField(max_length=32, verbose_name='TOKEN')
    expire_date = models.DateTimeField(verbose_name='过期时间')
    type = models.IntegerField(verbose_name='类型，0:access_token，1:refresh_token，2:service_token')

