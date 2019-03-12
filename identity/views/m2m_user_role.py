from op_keystone.base_view import M2MRelationView
from ..models import User, M2MUserRole
from assignment.models import Role


class UserToRoleView(M2MRelationView):
    """
    通过用户，对其所属的角色进行增、删、改、查
    """

    def __init__(self):
        from_model = User
        to_model = Role
        m2m_model = M2MUserRole
        super().__init__(from_model, to_model, m2m_model)
