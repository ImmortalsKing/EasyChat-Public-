from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Current Password:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': "current_password",
            'name': "current_password",
            'placeholder': 'Enter your current password...'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    new_password = forms.CharField(
        label='New Password:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': "new_password",
            'name': "new_password",
            'placeholder': 'Enter your new password...'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    password_confirm = forms.CharField(
        label='New Password Confirm:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': "new_password_confirm",
            'name': "new_password_confirm",
            'placeholder': 'Enter your new password again...'
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )

    def clean_password_confirm(self):
        new_password = self.cleaned_data.get('new_password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if new_password == password_confirm:
            return password_confirm
        raise ValidationError('Password and Password confirm are different!')


class AboutUserForm(forms.Form):
    about_user = forms.CharField(
        label='Current Password:',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'id': "about_user",
            'name': "about_user",
            'placeholder': 'Tell us about yourself...'
        }),
        validators=[
            validators.MaxLengthValidator(500)
        ]
    )