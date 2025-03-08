import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope.get("user", None)  # ✅ Évite une erreur si `user` est absent
#
#         if self.user and self.user.is_authenticated:
#             self.group_name = f"user_{self.user.id}"
#             await self.channel_layer.group_add(self.group_name, self.channel_name)
#             await self.accept()
#             logger.info(f"✅ WebSocket connecté pour l'utilisateur {self.user.username}")
#         else:
#             await self.close()
#             logger.warning("❌ Connexion WebSocket refusée : utilisateur non authentifié")
#
#     async def disconnect(self, close_code):
#         if self.user and self.user.is_authenticated:
#             await self.channel_layer.group_discard(self.group_name, self.channel_name)
#             logger.info(f"⛔ WebSocket déconnecté pour l'utilisateur {self.user.username}")
#
#     async def send_notification(self, event):
#         message = event["message"]
#         await self.send(text_data=json.dumps({"message": message}))
#         logger.info(f"📢 Notification envoyée : {message}")


User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token()

        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ WebSocket connecté pour {self.user.email}")  # ✅ Correction ici
        else:
            await self.close()
            print("❌ Connexion WebSocket refusée : utilisateur non authentifié")

    async def disconnect(self, close_code):
        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"⛔ WebSocket déconnecté pour {self.user.email}")  # ✅ Correction ici

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def get_user_from_token(self):
        query_string = self.scope["query_string"].decode()
        params = dict(param.split("=") for param in query_string.split("&") if "=" in param)

        token_key = params.get("token", None)
        if not token_key:
            return AnonymousUser()

        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()
