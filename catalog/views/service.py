from op_keystone.base_view import ResourceView
from ..models import Service


class ServicesView(ResourceView):
    """
    服务的增、删、改、查
    """

    def __init__(self):
        model = Service
        super().__init__(model)
