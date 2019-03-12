from op_keystone.base_view import M2MRelationView
from ..models import Role, Policy, M2MRolePolicy


class RoleToPolicyView(M2MRelationView):
    """
    通过角色，对将其关联的策略进行增、删、改、查
    """

    def __init__(self):
        from_model = Role
        to_model = Policy
        m2m_model = M2MRolePolicy
        super().__init__(from_model, to_model, m2m_model)


class PolicyToRoleView(M2MRelationView):
    """
    通过策略，对将其关联的角色进行增、删、改、查
    """

    def __init__(self):
        from_model = Policy
        to_model = Role
        m2m_model = M2MRolePolicy
        super().__init__(from_model, to_model, m2m_model)
