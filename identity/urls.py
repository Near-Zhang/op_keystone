from django.urls import path
from .views import *


urlpatterns = [
    path(r'users/', Users.as_view()),
]