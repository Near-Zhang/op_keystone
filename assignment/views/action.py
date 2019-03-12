from op_keystone.base_view import ResourceView
from ..models import Action


class ActionsView(ResourceView):
    """
    动作的增、删、改、查
    """

    def __init__(self):
        model = Action
        super().__init__(model)
