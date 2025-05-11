import base64
import json
import uuid
from datetime import datetime

import django
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from account_module.models import User, Group
from chat_module.models import UserChannel, Message

def truncate_filename(filename, max_length=10):
    if len(filename) > max_length:
        return filename[:max_length] + "..."
    return filename

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        try:
            user_channel = UserChannel.objects.get(user=self.scope.get('user'))
            user_channel.channel_name = self.channel_name
            user_channel.save()
        except:
            user_channel = UserChannel()
            user_channel.user = self.scope.get('user')
            user_channel.channel_name = self.channel_name
            user_channel.save()

        self.person_id = self.scope.get('url_route').get('kwargs').get('id')

    def receive(self, text_data):
        text_data = json.loads(text_data)

        other_user = User.objects.get(id=self.person_id)


        if text_data.get('type') == 'new_message':
            now = datetime.now()
            formatted_date = now.strftime('%b. %d, %Y %I:%M %p').lower().replace('am', 'a.m.').replace('pm',
                                                                                                       'p.m.')
            formatted_date = formatted_date.replace(formatted_date[:3], formatted_date[:3].title())
            avatar_sender = self.scope.get('user').avatar.url

            new_message = Message()
            new_message.from_who = self.scope.get('user')
            new_message.to_who = other_user
            new_message.message = text_data.get('message')
            new_message.date = now.date()
            new_message.time = now.time()
            new_message.has_been_seen = False
            new_message.save()

            message_id = new_message.id

            unseen_message_count = Message.objects.filter(
                from_who=other_user, to_who=self.scope.get('user'), has_been_seen=False
            ).count()

            receiver_sidebar_data = {
                "contact_id": self.scope.get('user').id,
                "contact_name": self.scope.get('user').display_name,
                "contact_avatar": self.scope.get('user').avatar.url,
                "last_message": new_message.message,
                "last_date": formatted_date,
                "unseen_message_count": unseen_message_count
            }

            sender_sidebar_data = {
                "contact_id": other_user.id,
                "contact_name": other_user.display_name,
                "contact_avatar": other_user.avatar.url,
                "last_message": new_message.message,
                "last_date": formatted_date,
                "unseen_message_count" : unseen_message_count
            }

            sender_data = {
                'type': 'receiver_function',
                'type_of_data': 'new_message',
                'id': message_id,
                'data': text_data.get('message'),
                'from': self.scope.get('user').display_name,
                'to': other_user.display_name,
                'avatar': avatar_sender,
                'date': formatted_date,
                'sender_id': self.scope.get('user').id,
                'receiver_id': other_user.id,
            }


            try:
                user_channel_name = UserChannel.objects.get(user=other_user)
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, sender_data)
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, {
                    'type': 'receiver_function',
                    'type_of_data': 'sidebar_updated',
                    'conversation': receiver_sidebar_data
                })
            except:
                pass


            try:
                user_channel_name = UserChannel.objects.get(user=self.scope.get('user'))
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, {
                    'type': 'receiver_function',
                    'type_of_data': 'sidebar_updated',
                    'conversation': sender_sidebar_data
                })
            except:
                pass


        elif text_data.get('type') == 'new_image':
            image_data = text_data.get('image')
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
            now = datetime.now()
            date = now.date()
            time = now.time()

            formatted_date = now.strftime('%b. %d, %Y %I:%M %p').lower().replace('am', 'a.m.').replace('pm',
                                                                                                       'p.m.')
            formatted_date = formatted_date.replace(formatted_date[:3], formatted_date[:3].title())
            sidebar_date = now.strftime('%d/%m/%Y')
            avatar_sender = self.scope.get('user').avatar.url

            new_message = Message()
            new_message.from_who = self.scope.get('user')
            new_message.to_who = other_user
            new_message.message = "image"
            new_message.image = image_file
            new_message.date = date
            new_message.time = time
            new_message.has_been_seen = False
            new_message.save()

            unseen_message_count = Message.objects.filter(
                from_who=other_user, to_who=self.scope.get('user'), has_been_seen=False
            ).count()

            receiver_sidebar_data = {
                "contact_id": self.scope.get('user').id,
                "contact_name": self.scope.get('user').display_name,
                "contact_avatar": self.scope.get('user').avatar.url,
                "last_message": "image",
                "last_date": sidebar_date,
                "unseen_message_count": unseen_message_count
            }

            sender_sidebar_data = {
                "contact_id": other_user.id,
                "contact_name": other_user.display_name,
                "contact_avatar": other_user.avatar.url,
                "last_message": "image",
                "last_date": sidebar_date,
                "unseen_message_count": unseen_message_count
            }

            try:
                user_channel_name = UserChannel.objects.get(user=other_user)
                data = {
                    'type': 'receiver_function',
                    'type_of_data': 'new_image',
                    'data': new_message.image.url,
                    'id': new_message.id,
                    'from': self.scope.get('user').display_name,
                    'to': other_user.display_name,
                    'avatar': avatar_sender,
                    'date': formatted_date,
                    'sender_id': self.scope.get('user').id,
                    'receiver_id': other_user.id,
                }
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)

                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, {
                    'type': 'receiver_function',
                    'type_of_data': 'sidebar_updated',
                    'conversation': receiver_sidebar_data
                })
            except:
                pass

            try:
                user_channel_name = UserChannel.objects.get(user=self.scope.get('user'))
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, {
                    'type': 'receiver_function',
                    'type_of_data': 'sidebar_updated',
                    'conversation': sender_sidebar_data
                })
            except:
                pass


        elif text_data.get('type') == 'new_file':
            file_data = text_data.get('file')
            filename = text_data.get('filename')
            truncated_filename = truncate_filename(filename, max_length=10)
            format, file_content = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file = ContentFile(base64.b64decode(file_content), name=filename)

            now = datetime.now()
            date = now.date()
            time = now.time()

            formatted_date = now.strftime('%b. %d, %Y %I:%M %p').lower().replace('am', 'a.m.').replace('pm',
                                                                                                       'p.m.')
            formatted_date = formatted_date.replace(formatted_date[:3], formatted_date[:3].title())
            sidebar_date = now.strftime('%d/%m/%Y')
            avatar_sender = self.scope.get('user').avatar.url

            new_message = Message()
            new_message.from_who = self.scope.get('user')
            new_message.to_who = other_user
            new_message.message = "file"
            new_message.file = file
            new_message.date = date
            new_message.time = time
            new_message.has_been_seen = False
            new_message.save()

            unseen_message_count = Message.objects.filter(
                from_who=other_user, to_who=self.scope.get('user'), has_been_seen=False
            ).count()

            receiver_sidebar_data = {
                "contact_id": self.scope.get('user').id,
                "contact_name": self.scope.get('user').display_name,
                "contact_avatar": self.scope.get('user').avatar.url,
                "last_message": "file",
                "last_date": sidebar_date,
                "unseen_message_count": unseen_message_count
            }

            sender_sidebar_data = {
                "contact_id": other_user.id,
                "contact_name": other_user.display_name,
                "contact_avatar": other_user.avatar.url,
                "last_message": "file",
                "last_date": sidebar_date,
                "unseen_message_count": unseen_message_count
            }

            try:
                user_channel_name = UserChannel.objects.get(user=other_user)
                data = {
                    'type': 'receiver_function',
                    'type_of_data': 'new_file',
                    'data': new_message.file.url,
                    'filename': truncated_filename,
                    'from': self.scope.get('user').display_name,
                    'to': other_user.display_name,
                    'avatar': avatar_sender,
                    'date': formatted_date,
                    'sender_id': self.scope.get('user').id,
                    'receiver_id': other_user.id,
                }
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)

                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, {
                    'type': 'receiver_function',
                    'type_of_data': 'sidebar_updated',
                    'conversation': receiver_sidebar_data
                })
            except:
                pass

            try:
                user_channel_name = UserChannel.objects.get(user=self.scope.get('user'))
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, {
                    'type': 'receiver_function',
                    'type_of_data': 'sidebar_updated',
                    'conversation': sender_sidebar_data
                })
            except:
                pass

        elif text_data.get('type') == 'i_have_seen_the_message':
            try:
                user_channel_name = UserChannel.objects.get(user=other_user)
                data = {
                    'type': 'receiver_function',
                    'type_of_data': 'the_messages_have_been_seen_by_the_other',
                }
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)

                messages_that_not_seen = Message.objects.filter(from_who=other_user,to_who=self.scope.get('user'))
                messages_that_not_seen.update(has_been_seen=True)
            except:
                pass

    def receiver_function(self,data_that_will_come_from_channel):
        data = json.dumps(data_that_will_come_from_channel)
        self.send(data)


class GroupChatConsumer(WebsocketConsumer):

    def connect(self):
        self.group_slug = self.scope.get('url_route').get('kwargs').get('slug')
        self.group_name = f"group_{self.group_slug}"

        user = self.scope.get('user')

        if not Group.objects.filter(slug__iexact=self.group_slug).exists():
            self.close()
            return

        if not User.objects.filter(group__slug__iexact=self.group_slug,id=user.id).exists():
            self.close()
            return


        async_to_sync(self.channel_layer.group_add)(self.group_name , self.channel_name)
        self.accept()


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)


    def receive(self, text_data):
        text_data = json.loads(text_data)

        user=self.scope.get('user')
        group = Group.objects.get(slug=self.group_slug)

        if text_data.get('type') == 'new_message':
            now = datetime.now()
            formatted_date = now.strftime('%b. %d, %Y %I:%M %p').lower().replace('am', 'a.m.').replace('pm', 'p.m.')
            formatted_date = formatted_date.replace(formatted_date[:3], formatted_date[:3].title())
            avatar_sender = user.avatar.url

            new_message = Message()
            new_message.group = group
            new_message.from_who = user
            new_message.message = text_data.get('message')
            new_message.date = now.date()
            new_message.time = now.time()
            new_message.save()

            message_id = new_message.id

            try:
                message_data = {
                    'type': 'receiver_function',
                    'type_of_data': 'new_message',
                    'data': text_data.get('message'),
                    'id': message_id,
                    'sender': user.display_name,
                    'avatar': avatar_sender,
                    'date': formatted_date,
                    'sender_id': user.id,
                    'group_slug': self.group_slug,
                }
                async_to_sync(self.channel_layer.group_send)(self.group_name, message_data)
            except:
                pass

            group_members = group.members.all()

            for member in group_members:
                unseen_message_count = Message.objects.filter(
                    group=group, has_been_seen=False
                ).exclude(from_who=member).count()

                sidebar_data = {
                    "group_slug": group.slug,
                    "group_name": group.title,
                    "group_avatar": group.avatar.url if group.avatar else None,
                    "last_message": new_message.message,
                    "sender": new_message.from_who.display_name,
                    "last_date": formatted_date,
                    "unseen_message_count": unseen_message_count
                }

                try:
                    async_to_sync(self.channel_layer.group_send)(self.group_name , {
                        'type': 'receiver_function',
                        'type_of_data': 'sidebar_updated',
                        'conversation': sidebar_data
                    })
                except:
                    pass

        elif text_data.get('type') == 'new_image':
            image_data = text_data.get('image')
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
            now = datetime.now()
            date = now.date()
            time = now.time()
            avatar_sender = user.avatar.url

            formatted_date = now.strftime('%b. %d, %Y %I:%M %p').lower().replace('am', 'a.m.').replace('pm',
                                                                                                   'p.m.')
            formatted_date = formatted_date.replace(formatted_date[:3], formatted_date[:3].title())

            new_message = Message()
            new_message.group = group
            new_message.from_who = user
            new_message.message = "image"
            new_message.image = image_file
            new_message.date = date
            new_message.time = time
            new_message.save()

            try:
                message_data = {
                    'type': 'receiver_function',
                    'type_of_data': 'new_image',
                    'data': new_message.image.url,
                    'id': new_message.id,
                    'sender': user.display_name,
                    'avatar': avatar_sender,
                    'date': formatted_date,
                    'sender_id': user.id,
                    'group_slug':self.group_slug,
                }
                async_to_sync(self.channel_layer.group_send)(self.group_name, message_data)
            except:
                pass

            group_members = group.members.all()

            for member in group_members:
                unseen_message_count = Message.objects.filter(
                    group=group, has_been_seen=False
                ).exclude(from_who=member).count()

                sidebar_data = {
                    "group_slug": group.slug,
                    "group_name": group.title,
                    "group_avatar": group.avatar.url if group.avatar else None,
                    "last_message": new_message.message,
                    "sender": new_message.from_who.display_name,
                    "last_date": formatted_date,
                    "unseen_message_count": unseen_message_count
                }

                try:
                    async_to_sync(self.channel_layer.group_send)(self.group_name, {
                        'type': 'receiver_function',
                        'type_of_data': 'sidebar_updated',
                        'conversation': sidebar_data
                    })
                except:
                    pass

        elif text_data.get('type') == 'new_file':
            file_data = text_data.get('file')
            filename = text_data.get('filename')
            truncated_filename = truncate_filename(filename, max_length=10)
            format, file_content = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file = ContentFile(base64.b64decode(file_content), name=filename)

            now = datetime.now()
            date = now.date()
            time = now.time()

            formatted_date = now.strftime('%b. %d, %Y %I:%M %p').lower().replace('am', 'a.m.').replace('pm',
                                                                                                       'p.m.')
            formatted_date = formatted_date.replace(formatted_date[:3], formatted_date[:3].title())
            avatar_sender = user.avatar.url

            new_message = Message()
            new_message.group = group
            new_message.from_who = user
            new_message.message = "file"
            new_message.file = file
            new_message.date = date
            new_message.time = time
            new_message.save()

            try:
                message_data = {
                    'type': 'receiver_function',
                    'type_of_data': 'new_file',
                    'data': new_message.file.url,
                    'filename': truncated_filename,
                    'sender': user.display_name,
                    'avatar': avatar_sender,
                    'date': formatted_date,
                    'sender_id': user.id,
                    'group_slug':self.group_slug,
                }
                async_to_sync(self.channel_layer.group_send)(self.group_name , message_data)
            except:
                pass

            group_members = group.members.all()

            for member in group_members:
                unseen_message_count = Message.objects.filter(
                    group=group, has_been_seen=False
                ).exclude(from_who=member).count()

                sidebar_data = {
                    "group_slug": group.slug,
                    "group_name": group.title,
                    "group_avatar": group.avatar.url if group.avatar else None,
                    "last_message": new_message.message,
                    "sender": new_message.from_who.display_name,
                    "last_date": formatted_date,
                    "unseen_message_count": unseen_message_count
                }

                try:
                    async_to_sync(self.channel_layer.group_send)(self.group_name, {
                        'type': 'receiver_function',
                        'type_of_data': 'sidebar_updated',
                        'conversation': sidebar_data
                    })
                except:
                    pass

        elif text_data.get('type') == 'i_have_seen_the_message':
            try:
                message_data = {
                    'type': 'receiver_function',
                    'type_of_data': 'the_messages_have_been_seen_by_the_other',
                }
                async_to_sync(self.channel_layer.group_send)(self.group_name, message_data)

                messages_that_not_seen = Message.objects.filter(group=group).exclude(from_who=user,has_been_seen=True)
                messages_that_not_seen.update(has_been_seen=True)
            except:
                pass

    def receiver_function(self,event):
        data = json.dumps(event)
        self.send(data)