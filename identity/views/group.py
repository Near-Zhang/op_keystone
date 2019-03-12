from op_keystone.base_view import ResourceView
from ..models import Group


class GroupsView(ResourceView):
    """
    用户组的增、删、改、查
    """

    def __init__(self):
        model = Group
        super().__init__(model)
