from op_keystone.base_view import ResourceView, MultiDeleteView
from ..models import Policy


class PoliciesView(ResourceView):
    """
    策略的增、删、改、查
    """

    def __init__(self):
        model = Policy
        super().__init__(model)


class MultiDeletePolicesView(MultiDeleteView):
    """
    策略的批量删除
    """

    def __init__(self):
        model = Policy
        super().__init__(model)