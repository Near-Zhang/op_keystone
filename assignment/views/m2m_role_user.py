from op_keystone.base_view import M2MRelationView
from ..models import Role
from identity.models import User, M2MUserRole


class RoleToUserView(M2MRelationView):
    """
    通过角色，对将其关联的用户进行增、删、改、查
    """

    def __init__(self):
        from_model = Role
        to_model = User
        m2m_model = M2MUserRole
        super().__init__(from_model, to_model, m2m_model)