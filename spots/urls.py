from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('spots/', views.spot_list, name='spot_list'),
    path('spots/<int:pk>/', views.spot_detail, name='spot_detail'),
    path('map/', views.map_view, name='map'),
    
    # 投稿・SNS関連 (main由来)
    path('posts/', views.post_list, name='post_list'), 
    path('posts/<int:post_id>/like/', views.toggle_post_like, name='post_like'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='post_comment'),
    
    path('api/check-location/', views.check_location, name='check_location'),
    path('ai_travel/', views.ai_travel, name='ai_travel'),
    path('favorite/<int:spot_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # 作品詳細 (ito由来)
    path('works/<int:work_id>/', views.work_detail, name='work_detail'),
    
    # ユーザープロフィール (main由来)
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
]