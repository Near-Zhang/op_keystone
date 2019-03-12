from op_keystone.base_view import ResourceView
from ..models import Project


class ProjectsView(ResourceView):
    """
    项目的增、删、改、查
    """

    def __init__(self):
        model = Project
        super().__init__(model)
