# ✅ ต้อง setup Django ก่อน import model
import os
import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_skt_center.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skt_center.settings')
django.setup()

import json
from typing import List
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from app_welcome_board.models.welcome_guest import WelcomeBoardGuest

@sync_to_async
def get_welcome_data():
    welcome: List[WelcomeBoardGuest] = list(WelcomeBoardGuest.objects.filter(isActive=True))
    if welcome:
        return {
            "media_type": "image",
            "path": [w.serialize() for w in welcome]
        }
    return {
        "media_type": "video",
        "path": [{"path": "guest-img/senikame-2.jpg"}]
    }


class WelcomeBoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'welcome_board'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        welcome_data = await get_welcome_data()
        await self.send(text_data=json.dumps(welcome_data))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"Received from client: {text_data}")

    async def send_welcome_board(self, event):
        await self.send(text_data=json.dumps({
            "media_type": event["media_type"],
            'path': event['path']
        }))
