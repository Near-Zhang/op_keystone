from op_keystone.exceptions import *
from op_keystone.base_view import BaseView
from utils import tools
from utils.dao import DAO
from django.conf import settings


class PolicyView(BaseView):
    domain_model = DAO('partition.models.Domain')
    role_modle = DAO('assignment.models.Policy')
    user_model = DAO('identity.models.User')
    token_model = DAO('credence.models.Token')

