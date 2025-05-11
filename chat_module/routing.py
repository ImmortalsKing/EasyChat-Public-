from django.urls import path

from chat_module import consumers

ASGI_urlpatterns = [
    path('websocket/chat/<int:id>',consumers.ChatConsumer.as_asgi()),
    path('websocket/group-chat/<slug:slug>',consumers.GroupChatConsumer.as_asgi()),
]