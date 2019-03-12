from op_keystone.base_view import ResourceView
from ..models import Domain


class DomainsView(ResourceView):
    """
    域的查、增、改、删
    """

    def __init__(self):
        model = Domain
        super().__init__(model)
