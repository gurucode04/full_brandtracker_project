from channels.generic.websocket import AsyncJsonWebsocketConsumer

class TrackerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('mentions', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('mentions', self.channel_name)

    async def mention_alert(self, event):
        await self.send_json(event['data'])
