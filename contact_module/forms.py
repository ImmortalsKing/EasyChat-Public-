from django import forms

from contact_module.models import ContactUs


class ContactUsModelForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['full_name','email','subject','message','image','response']
        widgets = {
            'full_name' : forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' : "Enter your name",
                'onfocus' : "this.placeholder = ''",
                'onblur' : "this.placeholder = 'Enter your name'"
            }),
            'email' : forms.EmailInput(attrs={
                'class' : 'form-control',
                'placeholder' : "Enter your email",
                'onfocus' : "this.placeholder = ''",
                'onblur' : "this.placeholder = 'Enter your email'"
            }),
            'subject' : forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' : "Enter your subject",
                'onfocus' : "this.placeholder = ''",
                'onblur' : "this.placeholder = 'Enter your subject'"
            }),
            'message' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' : 5,
                'placeholder' : "Enter your message",
                'onfocus' : "this.placeholder = ''",
                'onblur' : "this.placeholder = 'Enter your message'"
            }),
            'image' : forms.FileInput(),
            'response' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' : 5,
                'placeholder' : "Enter your message",
                'onfocus' : "this.placeholder = ''",
                'onblur' : "this.placeholder = 'Enter your message'"
            })
        }
        error_messages = {
            'full_name' : {
                'required': 'Enter your full name please',
            },
            'email': {
                'required': 'Enter your email please'
            },
            'subject': {
                'required': 'Enter your subject please'
            },
            'message': {
                'required': 'Enter your message please'
            },
        }