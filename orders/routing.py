from django.urls import path
from .watcher import OrderWatcher

websocket_urlpatterns = [
    path('ws/order-watcher', OrderWatcher.as_asgi())
]