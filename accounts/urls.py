from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ログイン画面 (Django標準の機能を使います)
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # ログアウト機能
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # サインアップ画面 (自作します)
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('users/<str:username>/', views.profile_public, name='profile_public'),

]