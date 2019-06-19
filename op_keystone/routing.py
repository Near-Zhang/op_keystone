from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
import catalog.routing


websocket_urlpatterns = [
    path(r'catalog/', catalog.routing.websocket_urlpatterns)
]


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': URLRouter(websocket_urlpatterns)
})
