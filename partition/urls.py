from django.urls import path
from .views import *


urlpatterns = [
    path(r'projects/', ProjectsView.as_view())
]