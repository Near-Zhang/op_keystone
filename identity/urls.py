from django.urls import path
from .views import *


urlpatterns = [
    path(r'users/', UsersView.as_view()),
    path(r'groups/', GroupsView.as_view()),
    path(r'login/', LoginView.as_view()),
    path(r'logout/', LogoutView.as_view())
]