from django.urls import path, re_path
from .views import *

urlpatterns = [
    path(r'roles/', RolesView.as_view()),
    path(r'policies/', PoliciesView.as_view()),
    re_path(r'^roles/(?P<role_uuid>\w+)/policies/$', RoleToPolicyView.as_view()),
    re_path(r'^policies/(?P<policy_uuid>\w+)/roles/$', PolicyToRoleView.as_view()),
    re_path(r'^roles/(?P<role_uuid>\w+)/users/$', RoleToUserView.as_view()),
    re_path(r'^roles/(?P<role_uuid>\w+)/groups/$', RoleToGroupView.as_view()),
    re_path(r'^actions/((?P<uuid>\w+)/)?$', ActionsView.as_view())
]
