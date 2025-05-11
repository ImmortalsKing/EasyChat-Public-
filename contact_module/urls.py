from django.urls import path
from . import views

urlpatterns = [
    path('',views.ContactUsView.as_view(),name='contact_us_page'),
    path('success/',views.ContactSuccessView.as_view(),name='contact_success_page'),
    path('responses/',views.ContactUsListView.as_view(),name='contact_list_page'),
    path('responses/<int:contact_id>',views.ContactUsDetailsView.as_view(),name='contact_details_page'),
]