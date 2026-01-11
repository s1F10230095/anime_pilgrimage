from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

# ▼▼▼ 追加：他のアプリ(spots)から称号モデルを読み込む ▼▼▼
from spots.models import UserTitle 

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_detail(request):
    profile = request.user.profile
    
    # 称号リスト
    user_titles = UserTitle.objects.filter(user=request.user).select_related('title').order_by('-obtained_at')

    # ▼▼▼ 追加：お気に入りした聖地リストを取得 ▼▼▼
    favorite_spots = request.user.favorite_spots.all()

    context = {
        'profile': profile,
        'user_titles': user_titles,
        'favorite_spots': favorite_spots, # ← 追加
    }
    return render(request, 'accounts/profile_detail.html', context)

@login_required
def profile_edit(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})

# accounts/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from spots.models import UserTitle

def profile_public(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = getattr(profile_user, 'profile', None)

    user_titles = UserTitle.objects.filter(
        user=profile_user
    ).select_related('title').order_by('-obtained_at')

    favorite_spots = profile_user.favorite_spots.all()

    return render(request, 'accounts/profile_public.html', {
        'profile_user': profile_user,
        'profile': profile,
        'user_titles': user_titles,
        'favorite_spots': favorite_spots,
    })
