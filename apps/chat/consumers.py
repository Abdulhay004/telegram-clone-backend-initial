import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': "Websocket ulanishi muvaffaqiyatli o'rnatildi."
        }))

    async def disconnect(self, close_code):
        print('Aloqa uzildi.')

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Xabarni qayta jo'natish
        await self.send(text_data=json.dumps({
            'message': message
        }))