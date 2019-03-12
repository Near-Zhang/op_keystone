from op_keystone.base_view import ResourceView
from ..models import Endpoint


class EndpointView(ResourceView):
    """
    端点的增、删、改、查
    """

    def __init__(self):
        model = Endpoint
        super().__init__(model)
