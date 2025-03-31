import json
from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync

from .models import Order

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
        data = json.loads(text_data)

        try:
            Order.objects.get(pk=data["id"]).mark_as_done()
            result = {
                "type": "order_marked_as_done",
                "success": True,
                "order_id": data["id"]
            }
        except Exception as e:
            result = {
                "type": "order_marked_as_done",
                "success": False,
                "message": str(e)
            }

        async_to_sync(self.channel_layer.group_send)(
            "order_watcher",
            {
                "type": "order_update",
                "message": result
            }
        )


    def order_update(self, event):
        self.send(text_data=json.dumps(event["message"]))