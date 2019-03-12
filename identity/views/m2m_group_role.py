from op_keystone.base_view import M2MRelationView
from ..models import Group, M2MGroupRole
from assignment.models import Role


class GroupToRoleView(M2MRelationView):
    """
    通过用户组，对其所属的角色进行增、删、改、查
    """

    def __init__(self):
        from_model = Group
        to_model = Role
        m2m_model = M2MGroupRole
        super().__init__(from_model, to_model, m2m_model)