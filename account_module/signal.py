from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, Group
from django.core.files import File
import os

@receiver(post_save, sender=User)
def set_default_avatar(sender, instance, created, **kwargs):
    if created and not instance.avatar:
        default_avatar_path = os.path.join(settings.BASE_DIR, 'staticfiles/images/avtar/face.png')

        with open(default_avatar_path, 'rb') as f:
            instance.avatar.save('face.png', File(f), save=False)
        instance.save()

@receiver(post_save, sender=Group)
def set_default_group_avatar(sender, instance, created, **kwargs):
    if created and not instance.avatar:
        default_avatar_path = os.path.join(settings.BASE_DIR, 'staticfiles/images/avtar/group-chat.png')

        with open(default_avatar_path, 'rb') as f:
            instance.avatar.save('group-chat.png', File(f), save=False)
        instance.save()
