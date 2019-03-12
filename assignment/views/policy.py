from op_keystone.base_view import ResourceView
from ..models import Policy


class PoliciesView(ResourceView):
    """
    策略的增、删、改、查
    """

    def __init__(self):
        model = Policy
        super().__init__(model)
