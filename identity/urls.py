from django.urls import path, re_path
from .views import *


urlpatterns = [
    path(r'users/', UsersView.as_view()),
    path(r'groups/', GroupsView.as_view()),
    re_path(r'users/(\w+)/groups', UserToGroupView.as_view()),
    re_path(r'groups/(\w+)/users', GroupToUserView.as_view()),
    path(r'login/', LoginView.as_view()),
    path(r'logout/', LogoutView.as_view()),
    path(r'password/', PasswordView.as_view())
]