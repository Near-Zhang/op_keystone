from django.urls import path, include


urlpatterns = [
    path(r'identity/', include('identity.urls')),
    path(r'partition/', include('partition.urls')),
    path(r'catalog/', include('catalog.urls'))
]