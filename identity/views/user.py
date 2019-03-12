from op_keystone.base_view import ResourceView
from ..models import User


class UsersView(ResourceView):
    """
    用户的增、删、改、查
    """

    def __init__(self):
        model = User
        super().__init__(model)
