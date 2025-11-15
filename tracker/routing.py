from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/mentions/', consumers.TrackerConsumer.as_asgi()),
]
