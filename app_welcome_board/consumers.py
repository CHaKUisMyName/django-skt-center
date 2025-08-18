import asyncio
from app_welcome_board.utils import get_all_welcome_data, get_filtered_welcome_data

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WelcomeBoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ยังไม่รู้ group รอรับ message แรกก่อน
        await self.accept()
        self.group_name = None
        self.keepalive_task = asyncio.create_task(self.keepalive())  # 👈 เพิ่ม keepalive

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"Received raw data: {text_data}")
        data = json.loads(text_data)
        print(f"Parsed data: {data}")

        # ลบ group เก่าถ้ามี เพื่อเปลี่ยน group
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        action = data.get("action")
        if action == "filtered":
            # --  สำหรับ หน้า show welcome board
            self.group_name = "filtered_guests"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            welcome_data = await get_filtered_welcome_data()
        else:
            # --  สำหรับ หน้า index guest
            self.group_name = "all_guests"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            welcome_data = await get_all_welcome_data()

        welcome_data["type"] = "send_welcome_board"
        await self.send(text_data=json.dumps(welcome_data))

    async def send_welcome_board(self, event):
        await self.send(text_data=json.dumps({
            "type": "send_welcome_board",
            "media_type": event["media_type"],
            'path': event['path']
        }))

    async def keepalive(self):
        """ส่ง ping ไปเรื่อยๆ ป้องกัน timeout"""
        while True:
            try:
                await asyncio.sleep(30)  # ทุก 30 วิ
                await self.send(text_data=json.dumps({"type": "ping"}))
            except Exception as e:
                print(f"Keepalive error: {e}")
                break
