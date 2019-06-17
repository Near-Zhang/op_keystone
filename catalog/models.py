from op_keystone.base_model import ResourceModel
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models
from utils.dao import DAO
from utils import tools


channel_layer = get_channel_layer()


class Service(ResourceModel):

    class Meta:
        verbose_name = '服务'
        db_table = 'service'

    # 必要字段
    name = models.CharField(max_length=64, unique=True, verbose_name='服务名')
    function = models.CharField(max_length=128, verbose_name='功能')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')

    def post_create(self):
        """
        创建后，生成一个永久服务 token，通知 channels
        """
        now = tools.get_datetime_with_tz()
        access_token = tools.generate_mapping_uuid(self.uuid, tools.datetime_to_humanized(now))
        DAO('credence.models.Token').create_obj(carrier=self.uuid, token=access_token,
                                                expire_date=now, type=2)

        async_to_sync(channel_layer.group_send)("catalog_notice", {
            'type': 'chat.message',
            'notice': 'service_created'
        })

    def post_update(self):
        """
        更新后，通知 channels
        """
        async_to_sync(channel_layer.group_send)("catalog_notice", {
            'type': 'chat.message',
            'notice': 'service_updated'
        })

    def pre_delete(self):
        """
        删除前，检查对象的对外关联
        :return:
        """
        DAO(Endpoint).delete_obj_qs(service=self.uuid)

    def post_delete(self):
        """
        删除后，，通知 channels
        :return:
        """
        async_to_sync(channel_layer.group_send)("catalog_notice", {
            'type': 'chat.message',
            'notice': 'service_deleted'
        })

    @staticmethod
    def get_field_opts(create=True):
        """
        获取创建对象需要的字段列表
        :return:
        """
        necessary = ['name', 'function']
        extra = ['enable', 'comment']
        senior_extra = []

        if create:
            return necessary, extra, senior_extra
        else:
            return necessary + extra, senior_extra

    @classmethod
    def get_default_query_keys(cls):
        return ['name', 'function'] + super().get_default_query_keys()


class Endpoint(ResourceModel):

    class Meta:
        verbose_name = '端点'
        db_table = 'endpoint'
        unique_together = ('ip', 'port')

    # 必要字段
    ip = models.CharField(max_length=64, verbose_name='IP')
    port = models.CharField(max_length=8, verbose_name='端口')
    service = models.CharField(max_length=32, verbose_name='服务UUID')

    # 附加字段
    enable = models.BooleanField(default=True, verbose_name='是否启用')
    comment = models.CharField(max_length=512, null=True, verbose_name='备注信息')

    def pre_create(self):
        """
        创建前，检查 service 是否存在
        """
        super().pre_create()
        DAO(Service).get_obj(uuid=self.service)

    def post_create(self):
        """
        创建后，通知 channels
        """
        async_to_sync(channel_layer.group_send)("catalog_notice", {
            'type': 'chat.message',
            'notice': 'endpoint_created'
        })

    def pre_update(self):
        """
        更新前，检查 service 是否存在
        """
        DAO(Service).get_obj(uuid=self.service)

    def post_update(self):
        """
        更新后，通知 channels
        """
        async_to_sync(channel_layer.group_send)("catalog_notice", {
            'type': 'chat.message',
            'notice': 'endpoint_updated'
        })

    def post_delete(self):
        """
        删除后，，通知 channels
        :return:
        """
        async_to_sync(channel_layer.group_send)("catalog_notice", {
            'type': 'chat.message',
            'notice': 'endpoint_deleted'
        })

    @staticmethod
    def get_field_opts(create=True):
        """
        获取创建对象需要的字段列表
        :return:
        """
        necessary = ['ip', 'port', 'service']
        extra = ['enable', 'comment']
        senior_extra = []

        if create:
            return necessary, extra, senior_extra
        else:
            return necessary + extra, senior_extra

    @classmethod
    def get_default_query_keys(cls):
        return ['ip', 'port', 'service'] + super().get_default_query_keys()

