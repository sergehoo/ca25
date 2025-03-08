"""
ASGI config for siade25 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os
#
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# from administration.routing import websocket_urlpatterns
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siade25.settings')
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(  # ✅ Ajout de l'authentification pour WebSockets
#         URLRouter(websocket_urlpatterns)
#     ),
# })
import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siade25.settings")

django.setup()  # ✅ Ajoute ceci avant d'importer `routing.py`

from administration.routing import websocket_urlpatterns  # ✅ Déplace après django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})