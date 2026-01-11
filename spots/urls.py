from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('spots/', views.spot_list, name='spot_list'),
    path('spots/<int:pk>/', views.spot_detail, name='spot_detail'),
    path('map/', views.map_view, name='map'),
    path('posts/', views.post_list, name='post_list'), 
    path('posts/create/', views.post_create, name='post_create'),
    path('api/check-location/', views.check_location, name='check_location'),
    path('ai_travel/', views.ai_travel, name='ai_travel'),
    path('favorite/<int:spot_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('works/<int:work_id>/', views.work_detail, name='work_detail'),
    ]

