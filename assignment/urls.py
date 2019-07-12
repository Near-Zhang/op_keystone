from django.urls import re_path
from .views import *

urlpatterns = [
    re_path(r'^roles/((?P<uuid>\w+)/)?$', RolesView.as_view()),
    re_path(r'^policies/((?P<uuid>\w+)/)?$', PoliciesView.as_view()),
    re_path(r'^roles/(?P<uuid>\w+)/policies/$', RoleToPolicyView.as_view()),
    re_path(r'^policies/(?P<uuid>\w+)/roles/$', PolicyToRoleView.as_view()),
    re_path(r'^roles/(?P<uuid>\w+)/users/$', RoleToUserView.as_view()),
    re_path(r'^roles/(?P<uuid>\w+)/groups/$', RoleToGroupView.as_view()),
    re_path(r'^actions/((?P<uuid>\w+)/)?$', ActionsView.as_view()),
    re_path(r'^role-tpls/((?P<uuid>\w+)/)?$', RoleTplsView.as_view()),
    re_path(r'^tpl-based-role/((?P<uuid>\w+)/)?$', TplBasedRole.as_view()),
    re_path(r'^multi-delete-policies/$', MultiDeletePolicesView.as_view()),
    re_path(r'^multi-delete-roles/$', MultiDeleteRoleView.as_view()),
    re_path(r'^tpl-flush-role/$', TplFlushRole.as_view()),
]
