from django.urls import re_path
from .views import *


urlpatterns = [
    re_path(r'^services/((?P<uuid>\w+)/)?$', ServicesView.as_view()),
    re_path(r'^endpoints/((?P<uuid>\w+)/)?$', EndpointView.as_view())
]