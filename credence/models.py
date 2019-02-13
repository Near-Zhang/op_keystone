from django.db import models
from utils.tools import datetime_to_humanized


class Token(models.Model):

    class Meta:
        verbose_name = 'TOKEN'
        db_table = 'token'

    # 必要字段
    user = models.CharField(max_length=32, verbose_name='用户UUID')
    token = models.CharField(max_length=32, verbose_name='TOKEN')
    expire_date = models.DateTimeField(verbose_name='过期时间')
    type = models.IntegerField(verbose_name='类型，0:access_token，2:refresh_token')

    def serialize(self):
        """
        对象序列化
        :return: dict
        """
        d = self.__dict__.copy()
        del d['_state']
        d['expire_date'] = datetime_to_humanized(d['expire_date'])
        return d

