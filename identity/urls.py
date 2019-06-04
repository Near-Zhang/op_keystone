from django.urls import path, re_path
from .views import *


urlpatterns = [
    re_path(r'^users/((?P<uuid>\w+)/)?$', UsersView.as_view()),
    re_path(r'^groups/((?P<uuid>\w+)/)?$', GroupsView.as_view()),
    re_path(r'^users/(?P<uuid>\w+)/groups/', UserToGroupView.as_view()),
    re_path(r'^groups/(?P<uuid>\w+)/users/', GroupToUserView.as_view()),
    re_path(r'^users/(?P<uuid>\w+)/roles/', UserToRoleView.as_view()),
    re_path(r'^groups/(?P<uuid>\w+)/roles/', GroupToRoleView.as_view()),
    path(r'login/', LoginView.as_view()),
    path(r'logout/', LogoutView.as_view()),
    path(r'refresh/', RefreshView.as_view()),
    path(r'password/', PasswordView.as_view()),
    path(r'captcha/', Captcha.as_view()),
    path(r'phone-captcha/', PhoneCaptcha.as_view()),
    path(r'email-captcha/', PhoneCaptcha.as_view()),
    path(r'auth/', Auth.as_view()),
    path(r'privilege-for-actions/', PrivilegeForActions.as_view())
]