# spots/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('spots/', views.spot_list, name='spot_list'),
    path('spots/<int:pk>/', views.spot_detail, name='spot_detail'),
    path('map/', views.map_view, name='map'),
    path('posts/', views.post_list, name='post_list'), 
<<<<<<< HEAD
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('posts/create/', views.post_create, name='post_create'), # 引数なし
=======
    path('posts/create/', views.post_create, name='post_create'),
    path('api/check-location/', views.check_location, name='check_location'),
>>>>>>> 086d4a2b25e4a5db5afcf5efdf8cb3520f69d8ec
]
