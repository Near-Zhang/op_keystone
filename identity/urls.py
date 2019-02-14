from django.urls import path, re_path
from .views import *


urlpatterns = [
    path(r'users/', UsersView.as_view()),
    path(r'groups/', GroupsView.as_view()),
    re_path(r'users/(?P<user_uuid>\w+)/groups', UserToGroupView.as_view()),
    re_path(r'groups/(?P<group_uuid>\w+)/users', GroupToUserView.as_view()),
    re_path(r'users/(?P<user_uuid>\w+)/roles', UserToRoleView.as_view()),
    re_path(r'groups/(?P<group_uuid>\w+)/roles', GroupToRoleView.as_view()),
    path(r'login/', LoginView.as_view()),
    path(r'logout/', LogoutView.as_view()),
    path(r'refresh/', RefreshView.as_view()),
    path(r'password/', PasswordView.as_view())
]