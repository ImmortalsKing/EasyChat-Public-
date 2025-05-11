from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from account_module.models import Group


class RegisterForm(forms.Form):
    code = forms.CharField(
        label='Code(that admin sent to you):',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': "code",
            'name': "code",
            'placeholder': 'Enter your code',
        }),
        validators=[
            validators.MaxLengthValidator(50)
        ]
    )
    email = forms.EmailField(
        label='Email:',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': "email",
            'name': "email",
            'placeholder': 'Enter your email'
        }),
        validators=[
            validators.MaxLengthValidator(200),
            validators.EmailValidator
        ]
    )
    display_name = forms.CharField(
        label='Display Name:',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': "display_name",
            'name': "display_name",
            'placeholder': 'Enter your display name'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    password = forms.CharField(
        label='Password:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': "password",
            'name': "password",
            'placeholder': 'Enter your password'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    password_confirm = forms.CharField(
        label='Password Confirm:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': "password_confirm",
            'name': "password_confirm",
            'placeholder': 'Enter your password again'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password == password_confirm:
            return password_confirm
        raise ValidationError('Password and Password confirm are different!')


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email:',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': "email",
            'name': "email",
            'placeholder': 'Enter Your email',
        }),
        validators=[
            validators.MaxLengthValidator(150),
            validators.EmailValidator,
        ]
    )
    password = forms.CharField(
        label='Password:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': "password",
            'name': "password",
            'placeholder': 'Enter your password'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

class InvitationCodeForm(forms.Form):
    code = forms.CharField(
        label='Code:',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': "code",
            'name': "code",
            'placeholder': 'Enter your desired code'
        }),
        validators=[
            validators.MaxLengthValidator(40)
        ]
    )

class GroupsForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title','avatar','about','members','is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Enter title...",
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Enter your title...'"
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': "Tell about your group...",
                'onfocus': "this.placeholder = ''",
                'onblur': "this.placeholder = 'Tell about your group...'"
            }),
            'avatar': forms.FileInput(),
            'members': forms.CheckboxSelectMultiple(attrs={
            }),
            'is_active': forms.CheckboxInput(attrs={
            })
        }