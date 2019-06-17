from channels.routing import URLRouter
from django.urls import re_path
from .consumers import *


urlpatterns = URLRouter([
    re_path(r'^ws/notice/((?P<uuid>\w+)/)?$', NoticeConsumer)
])