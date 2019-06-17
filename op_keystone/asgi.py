from channels.routing import ProtocolTypeRouter, URLRouter
import catalog.routing


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': URLRouter(
        catalog.routing.urlpatterns
    ),
})