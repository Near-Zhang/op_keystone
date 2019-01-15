from django.urls import path
from .views import *


urlpatterns = [
    path(r'services/', ServicesView.as_view()),
    path(r'endpoints/', EndpointView.as_view())
]