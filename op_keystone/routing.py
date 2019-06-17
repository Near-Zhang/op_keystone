from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
import catalog.routing


urlpatterns = [
    path(r'catalog/', catalog.routing.urlpatterns)
]


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': URLRouter(urlpatterns)
})
