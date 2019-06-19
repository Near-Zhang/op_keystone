from channels.generic.websocket import AsyncWebsocketConsumer
from op_keystone.exceptions import CustomException
from django.db import close_old_connections
from utils.dao import DAO
import json


class NoticeConsumer(AsyncWebsocketConsumer):
    """
    当 service 或 endpoint 有改动时，通知客户端
    """

    _user_model = DAO('identity.models.User')
    _group_name = 'catalog_notice'

    async def connect(self):
        user_uuid = self.scope['url_route']['kwargs']['uuid']

        try:
            close_old_connections()
            self._user_model.get_obj(uuid=user_uuid)

        except CustomException:
            await self.close()

        else:
            await self.channel_layer.group_add(
                self._group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self._group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        await self.close()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'notice': event['notice']
        }))
