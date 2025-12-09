from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 登録と同時にログイン状態にする
            login(request, user)
            return redirect('home')  # 登録後の移動先（トップページなど）
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_detail(request):
    profile = request.user.profile
    return render(request, 'accounts/profile_detail.html', {'profile': profile})

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

