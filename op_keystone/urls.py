from django.urls import path, include
from .base_view import BaseView
from .exceptions import *

urlpatterns = [
    path(r'identity/', include('identity.urls')),
    path(r'partition/', include('partition.urls')),
    path(r'catalog/', include('catalog.urls')),
    path(r'assignment/', include('assignment.urls'))
]


def handler404(request, **kwargs):
    try:
        raise PageNotFind(request.path)
    except CustomException as e:
        return BaseView().exception_to_response(e)

def handler500(request):
    try:
        raise InternalError()
    except CustomException as e:
        return BaseView().exception_to_response(e)

