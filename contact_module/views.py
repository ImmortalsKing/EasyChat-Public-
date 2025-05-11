from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, View, ListView, TemplateView

from contact_module.forms import ContactUsModelForm
from contact_module.models import ContactUs
from utils.email_service import send_email


class ContactUsView(CreateView):
    template_name = 'contact_module/contact_page.html'
    form_class = ContactUsModelForm
    success_url = '/contact-us/success/'

class ContactSuccessView(View):
    def get(self,request):
        return render(request,'contact_module/contact_success.html')


@method_decorator(staff_member_required,name='dispatch')
class ContactUsListComponent(ListView):
    template_name = 'contact_module/components/contact_list.html'
    model = ContactUs
    context_object_name = 'contacts'
    paginate_by = 6

@method_decorator(staff_member_required,name='dispatch')
class ContactUsListView(TemplateView):
    template_name = 'contact_module/contact_us_list.html'

@method_decorator(staff_member_required,name='dispatch')
class ContactUsDetailsView(View):
    def get(self,request,contact_id):
        feedback = ContactUs.objects.filter(id=contact_id).first()
        form = ContactUsModelForm(instance=feedback)
        context = {
            'form':form,
            'feedback':feedback,
        }
        return render(request,'contact_module/contact_us_details.html',context)

    def post(self,request,contact_id):
        feedback = ContactUs.objects.filter(id=contact_id).first()
        form = ContactUsModelForm(request.POST,instance=feedback)
        if form.is_valid():
            response = form.cleaned_data.get('response')
            if response != "":
                feedback.response = response
                feedback.is_read_by_admin = True
                form.save()
                feedback.save()
                send_email('Easychat-thanks for feedback',feedback.email,{'feedback':feedback},'emails/feedback_response.html')
                messages.info(request,
                              'Email has been sent successfully.')
                return redirect(reverse('contact_list_page'))
            else:
                form.save()
                return redirect(reverse('contact_list_page'))
        context = {
            'form': form,
            'feedback': feedback,
        }
        return render(request, 'contact_module/contact_us_details.html', context)



