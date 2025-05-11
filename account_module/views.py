from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.generic import View, ListView, TemplateView

from account_module.forms import RegisterForm, LoginForm, InvitationCodeForm, GroupsForm
from account_module.models import InvitationCode, User, Group
from utils.decorator import unblocked_user_required


@method_decorator(staff_member_required, name='dispatch')
class GenerateInviteCodeView(View):
    def get(self, request):
        code = None
        form = InvitationCodeForm(request.POST)
        context = {
            'form': form,
            'code': code
        }
        return render(request, 'account_module/generate_code.html', context)

    def post(self, request):
        code = None
        form = InvitationCodeForm(request.POST)
        if 'submit_1' in request.POST:
            if form.is_valid():
                code = form.cleaned_data.get('code')
                InvitationCode.objects.create(code=code)
        if 'submit_2' in request.POST:
            code = InvitationCode.generate_code()
            InvitationCode.objects.create(code=code)
        context = {
            'form': form,
            'code': code
        }
        return render(request, 'account_module/generate_code.html', context)

@method_decorator(unblocked_user_required,name='dispatch')
class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('blank_chat_page'))
        else:
            form = RegisterForm()
            context = {
                'form': form
            }
            return render(request, 'account_module/register.html', context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('blank_chat_page'))
        else:
            form = RegisterForm(request.POST)
            if form.is_valid():
                user_code = form.cleaned_data.get('code')
                email = form.cleaned_data.get('email')
                user_display_name = form.cleaned_data.get('display_name')
                password = form.cleaned_data.get('password')
                invitation = InvitationCode.objects.filter(code__iexact=user_code, invited_user__isnull=True).first()
                user_exists = User.objects.filter(email__iexact=email).exists()
                if invitation is None:
                    form.add_error('code', 'The Code is wrong or you have registered before.')
                elif user_exists:
                    form.add_error('email', 'The Email is already registered.')
                else:
                    new_user = User(
                        display_name=user_display_name,
                        is_active=True,
                        email=email,
                        username=email,
                    )
                    new_user.set_password(password)
                    new_user.save()

                    invitation.invited_user = new_user
                    invitation.save()
                    login(request, new_user)
                    return redirect(reverse('blank_chat_page'))

            else:
                form.add_error('code', 'Something went wrong...')

            context = {
                'form': form
            }
            return render(request, 'account_module/register.html', context)

@method_decorator(unblocked_user_required,name='dispatch')
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('blank_chat_page'))
        else:
            form = LoginForm()
            context = {
                'form': form
            }
            return render(request, 'account_module/login.html', context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('blank_chat_page'))

        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user_password = form.cleaned_data.get('password')


            user = User.objects.filter(email__iexact=email).first()
            if user and user.check_password(user_password):
                login(request, user)
                return redirect(reverse('blank_chat_page'))
            else:
                form.add_error('email', 'Entered email or password is incorrect.')

        return render(request, 'account_module/login.html', {'form': form})

@method_decorator([login_required,unblocked_user_required],name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('main_page'))

@method_decorator(staff_member_required, name='dispatch')
class UsersListView(ListView):
    template_name = 'account_module/users_list.html'
    model = User
    context_object_name = 'users'
    paginate_by = 6

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = super().get_queryset()
        query = query.order_by('-is_superuser','date_joined')
        return query

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        person = User.objects.filter(id=user_id).first()
        if "block_user" in request.POST:
            if person is not None:
                person.is_blocked = True
                person.save()
                return redirect(reverse('users_list_page'))
            else:
                pass
        elif "unblock_user" in request.POST:
            if person is not None:
                person.is_blocked = False
                person.save()
                return redirect(reverse('users_list_page'))
            else:
                pass


class BlockPageView(TemplateView):
    template_name = 'account_module/block_page.html'


@method_decorator(staff_member_required,name='dispatch')
class GroupsListComponent(ListView):
    template_name = 'account_module/components/group_list_component.html'
    model = Group
    context_object_name = 'groups'
    paginate_by = 5


@method_decorator(staff_member_required,name='dispatch')
class GroupsListView(View):
    def get(self,request):
        form = GroupsForm()
        context = {
            'form':form
        }
        return render(request,'account_module/groups_list.html',context)

    def generate_unique_slug(self, title):
        base_slug = slugify(title)
        slug = base_slug
        count = 1
        while Group.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{get_random_string(4)}"
            count += 1
        return slug


    def post(self,request):
        form = GroupsForm(request.POST, request.FILES)
        if 'create_group' in request.POST:
            if form.is_valid():
                group_title = form.cleaned_data.get('title')
                group_avatar = form.cleaned_data.get('avatar')
                group_members = form.cleaned_data.get('members')
                group_is_active = form.cleaned_data.get('is_active')
                group_about = form.cleaned_data.get('about')

                group_slug = self.generate_unique_slug(group_title)

                new_group = Group.objects.create(
                    title=group_title,
                    avatar=group_avatar,
                    is_active=group_is_active,
                    about=group_about,
                    slug=group_slug
                )

                new_group.members.set(group_members)
                return redirect(reverse('group_chat_page', kwargs={'slug': group_slug}))

        elif 'delete_group_btn' in request.POST:
            group_slug = request.POST.get('group_slug')
            try:
                selected_group = Group.objects.get(slug=group_slug)
                selected_group.delete()
            except:
                pass
            return redirect(reverse('groups_list_page'))


        context = {
            'form': form
        }
        return render(request, 'account_module/groups_list.html', context)


@method_decorator(staff_member_required,name='dispatch')
class GroupsEditView(View):
    def get(self, request , slug):
        group = Group.objects.get(slug=slug)
        form = GroupsForm(instance=group)
        context = {
            'form': form,
            'group': group,
        }
        return render(request, 'account_module/groups_list_edit.html', context)


    def post(self, request , slug):
        group = Group.objects.get(slug=slug)
        form = GroupsForm(request.POST, request.FILES , instance=group)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('groups_edit_page' , kwargs={'slug':slug}))

        context = {
            'form': form,
            'group': group,
        }
        return render(request, 'account_module/groups_list_edit.html', context)

