from op_keystone.base_view import M2MRelationView
from ..models import User, Group, M2MUserGroup


class UserToGroupView(M2MRelationView):
    """
    通过用户，对其关联的组进行增、删、改、查
    """

    def __init__(self):
        from_model = User
        to_model = Group
        m2m_model = M2MUserGroup
        super().__init__(from_model, to_model, m2m_model)


class GroupToUserView(M2MRelationView):
    """
    通过用户组，对其关联的用户进行增、删、改、查
    """

    def __init__(self):
        from_model = Group
        to_model = User
        m2m_model = M2MUserGroup
        super().__init__(from_model, to_model, m2m_model)
