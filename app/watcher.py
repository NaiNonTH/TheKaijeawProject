import json
from channels.generic.websocket import WebsocketConsumer

from django.db.models import signals
from .models import Order

class OrderWatcher(WebsocketConsumer):
    def connect(self):
        self.accept()

        print("opened")

        self.send(text_data=json.dumps({
            "test": "Hello, world"
        }))

    def disconnect(self, code):
        print("closed")

    def receive(self, text_data=None, bytes_data=None):
        return super().receive(text_data, bytes_data)