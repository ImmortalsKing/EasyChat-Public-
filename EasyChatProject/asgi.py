"""
ASGI config for EasyChatProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyChatProject.settings')
django.setup()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import chat_module
from chat_module import routing



application = ProtocolTypeRouter(
    {
        'http' : get_asgi_application(),
        'websocket' : AuthMiddlewareStack(URLRouter(chat_module.routing.ASGI_urlpatterns))
    }
)
