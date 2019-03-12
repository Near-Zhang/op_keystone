from op_keystone.base_view import M2MRelationView
from ..models import Role
from identity.models import Group, M2MGroupRole


class RoleToGroupView(M2MRelationView):
    """
    通过角色，对将其关联的用户组进行增、删、改、查
    """

    def __init__(self):
        from_model = Role
        to_model = Group
        m2m_model = M2MGroupRole
        super().__init__(from_model, to_model, m2m_model)
