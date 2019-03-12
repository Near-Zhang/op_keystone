from django.urls import re_path
from .views import *


urlpatterns = [
    re_path(r'^projects/((?P<uuid>\w+)/)?$', ProjectsView.as_view()),
    re_path(r'^domains/((?P<uuid>\w+)/)?$', DomainsView.as_view())
]