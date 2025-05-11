import os
import random

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Q, OuterRef, Subquery, Count
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView, ListView

from account_module.models import User, Country, Group
from chat_module.forms import ChangePasswordForm, AboutUserForm
from chat_module.models import Message, UserChannel, GalleryRoom, Gallery
from utils.decorator import unblocked_user_required

@method_decorator(unblocked_user_required,name='dispatch')
class BlankChatModuleView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'chat_module/blank_messenger.html')
        else:
            return redirect(reverse('main_page'))

@method_decorator([login_required,unblocked_user_required],name='dispatch')
class ChatModuleView(View):
    def get(self, request, id):
        if request.user.id == id:
            return redirect(reverse('blank_chat_page'))
        else:
            person = User.objects.filter(id=id).first()
            me = request.user

            messages = Message.objects.filter(Q(from_who=me, to_who=person) | Q(from_who=person, to_who=me)).order_by(
                'date', 'time')

            user_channel_name, created = UserChannel.objects.get_or_create(user=person)

            if created or not user_channel_name.channel_name:
                user_channel_name.channel_name = f"default_channel_{person.id}"
                user_channel_name.save()

            data = {
                'type': 'receiver_function',
                'type_of_data': 'the_messages_have_been_seen_by_the_other',
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(user_channel_name.channel_name, data)

            messages_that_not_seen = Message.objects.filter(from_who=person, to_who=me)
            messages_that_not_seen.update(has_been_seen=True)

            for message in messages:
                if message.file:
                    message.file_url = message.file.url
                    message.file_name = message.file.name.split('/')[-1]

            context = {
                'person': person,
                'me': me,
                'chat_messages': messages,
            }

            return render(request, 'chat_module/messenger.html', context)

    def post(self,request,id):
        person = User.objects.filter(id=id).first()
        message_id = request.POST.get('message_id')
        message = Message.objects.filter(id=message_id).first()
        if "block_user" in request.POST:
            if person is not None:
                person.is_blocked = True
                person.save()
                return redirect(reverse('chat_page',kwargs={'id':id}))
            else:
                pass
        elif "unblock_user" in request.POST:
            if person is not None:
                person.is_blocked = False
                person.save()
                return redirect(reverse('chat_page',kwargs={'id':id}))
            else:
                pass

        elif "message_delete" in request.POST:
            if message is not None:
                message.delete()
                return redirect(reverse('chat_page',kwargs={'id':id}))
            else:
                pass

        me = request.user

        messages = Message.objects.filter(Q(from_who=me, to_who=person) | Q(from_who=person, to_who=me)).order_by(
            'date', 'time')

        user_channel_name, created = UserChannel.objects.get_or_create(user=person)

        if created or not user_channel_name.channel_name:
            user_channel_name.channel_name = f"default_channel_{person.id}"
            user_channel_name.save()

        data = {
            'type': 'receiver_function',
            'type_of_data': 'the_messages_have_been_seen_by_the_other',
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(user_channel_name.channel_name, data)

        messages_that_not_seen = Message.objects.filter(from_who=person, to_who=me)
        messages_that_not_seen.update(has_been_seen=True)

        for message in messages:
            if message.file:
                message.file_url = message.file.url
                message.file_name = message.file.name.split('/')[-1]

        context = {
            'person': person,
            'me': me,
            'chat_messages': messages,
        }

        return render(request, 'chat_module/messenger.html', context)


@method_decorator([login_required,unblocked_user_required],name='dispatch')
class GroupChatView(View):
    def get(self, request, slug):
        members:User = User.objects.filter(group__slug__iexact=slug)
        not_members:User = User.objects.exclude(id__in=members.values_list("id",flat=True))
        sender = request.user
        users = User.objects.all().exclude(id=sender.id)
        group = Group.objects.filter(is_active=True,slug__iexact=slug).first()


        group_messages = Message.objects.filter(Q(from_who=sender, group=group) | Q(group=group) & ~Q(from_who=sender)).order_by('date', 'time')

        for message in group_messages:
            if message.file:
                message.file_url = message.file.url
                message.file_name = message.file.name.split('/')[-1]

        group_name = f"group_{slug}"

        message_data = {
            'type': 'receiver_function',
            'type_of_data': 'the_messages_have_been_seen_by_the_other',
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message_data)

        messages_that_not_seen = Message.objects.filter(group=group).exclude(from_who=sender)
        for message in messages_that_not_seen:
            if message.from_who != sender:
                message.has_been_seen = True
                message.save()


        context = {
            'members': members,
            'not_members': not_members,
            'sender':sender,
            'group':group,
            'group_messages': group_messages,
            'users':users,
        }

        return render(request, 'chat_module/messenger.html', context)

    def post(self, request, slug):
        group = Group.objects.get(slug=slug)
        if 'remove_btn' in request.POST:
            user_id = request.POST.get('user_id')
            if user_id:
                try:
                    selected_user = User.objects.get(id=user_id)
                    group.members.remove(selected_user)
                except User.DoesNotExist:
                    print(f"user with {user_id} doesn't exist")
            return redirect(reverse('group_chat_page', kwargs={'slug': slug}))

        elif 'add_btn' in request.POST:
            user_id = request.POST.get('user_id')
            if user_id:
                try:
                    selected_user = User.objects.get(id=user_id)
                    group.members.add(selected_user)
                except User.DoesNotExist:
                    print(f"user with {user_id} doesn't exist")
            return redirect(reverse('group_chat_page', kwargs={'slug': slug}))

        elif 'delete_group' in request.POST:
            try:
                group.delete()
            except:
                pass
            return redirect(reverse('blank_chat_page'))

        elif "group_message_delete" in request.POST:
            message_id = request.POST.get('group_message_id')
            message = Message.objects.get(id=message_id)
            if message is not None:
                message.delete()
                return redirect(reverse('group_chat_page',kwargs={'slug':slug}))
            else:
                pass

        members: User = User.objects.filter(group__slug__iexact=slug)
        not_members: User = User.objects.exclude(id__in=members.values_list("id", flat=True))
        sender = request.user
        users = User.objects.all().exclude(id=sender.id)
        group = Group.objects.filter(is_active=True, slug__iexact=slug).first()

        group_messages = Message.objects.filter(
            Q(from_who=sender, group=group) | Q(group=group) & ~Q(from_who=sender)).order_by('date', 'time')

        for message in group_messages:
            if message.file:
                message.file_url = message.file.url
                message.file_name = message.file.name.split('/')[-1]

        group_name = f"group_{slug}"

        message_data = {
            'type': 'receiver_function',
            'type_of_data': 'the_messages_have_been_seen_by_the_other',
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message_data)

        messages_that_not_seen = Message.objects.filter(group=group).exclude(from_who=sender, has_been_seen=True)
        messages_that_not_seen.update(has_been_seen=True)

        context = {
            'members': members,
            'not_members': not_members,
            'sender': sender,
            'group': group,
            'group_messages': group_messages,
            'users': users,
        }

        return render(request, 'chat_module/messenger.html', context)


@method_decorator(unblocked_user_required,name='dispatch')
class MainPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('blank_chat_page'))
        else:
            return render(request, 'chat_module/main_page.html')


@csrf_exempt
@login_required
@unblocked_user_required
def update_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        country_name = request.POST.get('country')
        request.user.display_name = username
        try:
            country = Country.objects.get(name=country_name)
            request.user.country = country
        except Country.DoesNotExist:
            return JsonResponse({'error': 'country is invalid.'}, status=400)

        request.user.save()
        return JsonResponse({'message': 'Profile has been updated successfully.', 'new_flag_url': country.logo.url},
                            status=200)

    return JsonResponse({'error': 'Requested method is invalid.'}, status=400)


@csrf_exempt
@login_required
@unblocked_user_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar_file = request.FILES['avatar']

        file_path = os.path.join('avatars', avatar_file.name)
        saved_path = default_storage.save(file_path, ContentFile(avatar_file.read()))

        request.user.avatar = saved_path
        request.user.save()

        new_avatar_url = request.user.avatar.url
        return JsonResponse({
            'success': True,
            'new_avatar_url': new_avatar_url
        })

    return JsonResponse({'success': False, 'error': 'File has not been sent.'}, status=400)


@method_decorator([login_required,unblocked_user_required],name='dispatch')
class ChangePasswordView(View):
    def get(self, request):
        form = ChangePasswordForm()
        next_url = request.META.get('HTTP_REFERER', reverse('main_page'))
        context = {
            'form': form,
            'next': next_url,
        }
        return render(request, 'chat_module/components/change_password_component.html', context)

    def post(self, request):
        form = ChangePasswordForm(request.POST)
        next_url = request.META.get('HTTP_REFERER', reverse('main_page'))
        if form.is_valid():
            user = request.user
            user_current_password = form.cleaned_data.get('current_password')
            user_new_password = form.cleaned_data.get('new_password')
            is_password_correct = user.check_password(user_current_password)
            if is_password_correct:
                user.set_password(user_new_password)
                user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Your password was successfully updated.')
                return redirect(next_url)
            else:
                messages.error(request, 'Current password is incorrect.')
                return redirect(next_url)
        context = {
            'form': form,
            'next': next_url,
        }
        return render(request, 'chat_module/components/change_password_component.html', context)

@method_decorator([login_required,unblocked_user_required],name='dispatch')
class AboutUserView(View):
    def get(self, request):
        user = request.user
        form = AboutUserForm(initial={'about_user':user.about_user})
        next_url = request.META.get('HTTP_REFERER', reverse('main_page'))
        context = {
            'form': form,
            'next': next_url,
        }
        return render(request, 'chat_module/components/about_user.html', context)

    def post(self, request):
        form = AboutUserForm(request.POST)
        next_url = request.META.get('HTTP_REFERER', reverse('main_page'))
        if form.is_valid():
            user = request.user
            about_user = form.cleaned_data.get('about_user')
            if about_user is not None:
                user.about_user = about_user
                user.save()
                messages.success(request, '"About me" field was successfully updated.')
                return redirect(next_url)
            else:
                messages.error(request, 'Something went wrong!')
                return redirect(next_url)
        context = {
            'form': form,
            'next': next_url,
        }
        return render(request, 'chat_module/components/about_user.html', context)


class SidebarComponent(View):
    def get(self, request):
        contacts = User.objects.all().exclude(id=request.user.id)
        me = request.user
        current_contact_id = self.kwargs.get('id')
        countries = Country.objects.all()
        gallery_rooms = GalleryRoom.objects.filter(is_active=True)
        groups = Group.objects.filter(is_active=True)
        no_msg_groups = Group.objects.filter(is_active=True,messages__isnull=True)

        for group in no_msg_groups:
            members = list(group.members.all())
            random.shuffle(members)
            group.selected_members = members[:2]

        last_messages_subquery = Message.objects.filter(
            Q(from_who=OuterRef('pk'), to_who=me) | Q(from_who=me, to_who=OuterRef('pk'))
        ).order_by('-date', '-time').values('message', 'date', 'time')[:1]

        unseen_message_count_subquery = Message.objects.filter(
            from_who=OuterRef('pk'), to_who=me, has_been_seen=False
        ).values('from_who').annotate(count=Count('id')).values('count')

        contacts_with_last_message = contacts.annotate(
            last_message_text=Subquery(last_messages_subquery.values('message')),
            last_date=Subquery(last_messages_subquery.values('date')),
            last_time=Subquery(last_messages_subquery.values('time')),
            last_seen=Subquery(last_messages_subquery.values('has_been_seen')),
            last_message_sender=Subquery(last_messages_subquery.values('from_who')),
            unseen_message_count=Subquery(unseen_message_count_subquery, output_field=models.IntegerField()),
        )

        last_conversations = []
        for contact in contacts_with_last_message:
            if contact.last_message_text:
                last_conversations.append({
                    'contact': contact,
                    'last_message': {
                        'last_message_text': contact.last_message_text,
                        'last_date': contact.last_date,
                        'last_time': contact.last_time,
                        'last_seen': contact.last_seen,
                        'last_message_sender': contact.last_message_sender,
                        'unseen_message_count': contact.unseen_message_count or 0,
                    },
                })

        last_conversations = sorted(
            last_conversations,
            key=lambda x: x['last_message']['last_time'],
            reverse=False
        )

        last_group_messages_subquery = Message.objects.filter(
            group=OuterRef('pk')
        ).order_by('-date', '-time')

        groups_with_last_message = groups.annotate(
            last_message_text=Subquery(last_group_messages_subquery.values('message')[:1]),
            last_date=Subquery(last_group_messages_subquery.values('date')[:1]),
            last_time=Subquery(last_group_messages_subquery.values('time')[:1]),
            last_message_sender=Subquery(last_group_messages_subquery.values('from_who')[:1]),
        )

        for group in groups_with_last_message:
            group.last_message_sender = User.objects.filter(id=group.last_message_sender).first()

        group_last_conversations = []
        for group in groups_with_last_message:
            if group.last_message_text:
                group_last_conversations.append({
                    'type': 'group',
                    'group': group,
                    'last_message': {
                        'last_message_text': group.last_message_text,
                        'last_date': group.last_date,
                        'last_time': group.last_time,
                        'last_message_sender': group.last_message_sender,
                    },
                })

        for group in groups_with_last_message:
            members = list(group.members.all())
            random.shuffle(members)
            group.selected_members = members[:2]

        group_last_conversations = sorted(
            group_last_conversations,
            key=lambda x: x['last_message']['last_time'],
            reverse=False
        )



        context = {
            'me': me,
            'contacts': contacts,
            'last_conversations': last_conversations,
            'group_last_conversations': group_last_conversations,
            'current_contact_id': current_contact_id,
            'countries': countries,
            'gallery_rooms':gallery_rooms,
            'groups':groups,
            'no_msg_groups':no_msg_groups,
        }
        return render(request, 'chat_module/components/sidebar_component.html', context)


class ContactTodoComponent(TemplateView):
    template_name = 'chat_module/components/contacts_todo.html'

@method_decorator([login_required,unblocked_user_required],name='dispatch')
class GalleryView(ListView):
    template_name = 'chat_module/gallery.html'
    model = Gallery
    context_object_name = 'galleries'
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        gallery_room = GalleryRoom.objects.filter(slug=slug,is_active=True).first()
        if gallery_room is not None:
            return Gallery.objects.filter(room=gallery_room).order_by('-date')
        else:
            return Http404

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        slug = self.kwargs.get('slug')
        context['room'] = GalleryRoom.objects.filter(slug=slug).first()
        context['request'] = self.request
        return context

    def post(self,request , *args, **kwargs):
        if 'delete_gallery' in request.POST:
            gallery_id = request.POST.get('gallery_id')
            gallery = Gallery.objects.filter(id=gallery_id).first()
            slug = self.kwargs.get('slug')
            if gallery is not None:
                gallery.delete()
                return redirect(reverse('gallery_page',kwargs={'slug':slug}))
            else:
                pass

        elif 'add_gallery' in request.POST:
            image = request.FILES.get('gallery_image')
            caption = request.POST.get('caption')
            room_id = request.POST.get('gallery_room')
            slug = self.kwargs.get('slug')

            if not image:
                return HttpResponse("No image uploaded", status=400)

            try:
                room = GalleryRoom.objects.get(id=room_id)
                gallery = Gallery(image=image, caption=caption, room=room)
                gallery.save()
                return redirect(reverse('gallery_page', kwargs={'slug': slug}))
            except:
                return HttpResponse("Invalid Gallery Room", status=400)

        return super().post(request, *args, **kwargs)


