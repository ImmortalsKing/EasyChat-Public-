from django.urls import path

from chat_module import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
    path('chat/', views.BlankChatModuleView.as_view(), name='blank_chat_page'),
    path('chat/<int:id>/', views.ChatModuleView.as_view(), name='chat_page'),
    path('group-chat/<slug:slug>', views.GroupChatView.as_view(), name='group_chat_page'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-avatar/', views.update_avatar, name='update_avatar'),
    path('change-password/',views.ChangePasswordView.as_view(),name='change_password'),
    path('about-me/',views.AboutUserView.as_view(),name='about_me'),
    path('gallery/<slug:slug>/',views.GalleryView.as_view(),name='gallery_page'),
]
