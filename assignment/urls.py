from django.urls import path
from .views import *

urlpatterns = [
    path(r'role/', RoleView.as_view()),
    path(r'policy/', PolicyView.as_view())
]
