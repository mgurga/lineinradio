from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/radio/", consumers.RadioConsumer.as_asgi()),
]
