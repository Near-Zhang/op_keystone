from django.urls import path, include


urlpatterns = [
    path(r'identity/', include('identity.urls')),
]
