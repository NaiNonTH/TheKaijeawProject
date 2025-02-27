import json
from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync

class OrderWatcher(WebsocketConsumer):
    def connect(self):
        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            "order_watcher",
            self.channel_name
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            "order_watcher",
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        return super().receive(text_data, bytes_data)

    def order_update(self, event):
        self.send(text_data=json.dumps(event["message"]))