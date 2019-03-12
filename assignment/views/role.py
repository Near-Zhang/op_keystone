from op_keystone.base_view import ResourceView
from ..models import Role


class RolesView(ResourceView):
    """
    角色的增、删、改、查
    """

    def __init__(self):
        model = Role
        super().__init__(model)
