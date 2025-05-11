from django.urls import path

from account_module import views

urlpatterns = [
    path('generate-code',views.GenerateInviteCodeView.as_view(),name='generate_code_page'),
    path('register',views.RegisterView.as_view(),name='register_page'),
    path('login',views.LoginView.as_view(),name='login_page'),
    path('logout',views.LogoutView.as_view(),name='logout_page'),
    path('users-list',views.UsersListView.as_view(),name='users_list_page'),
    path('block-page',views.BlockPageView.as_view(),name='blocked_page'),
    path('groups-list',views.GroupsListView.as_view(),name='groups_list_page'),
    path('groups-list/<slug:slug>',views.GroupsEditView.as_view(),name='groups_edit_page'),
]