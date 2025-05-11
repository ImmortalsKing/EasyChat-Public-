import re

from django import template

register = template.Library()

@register.filter(name='match_chat_url')
def match_chat_url(value):
    return bool(re.match(r"^/chat/\d+/$", value))