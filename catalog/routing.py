from django.urls import path, re_path
from .consumers import *


urlpatterns = [
    re_path(r'^catalog/ws/notice/((?P<uuid>\w+)/)?$', NoticeConsumer)
]