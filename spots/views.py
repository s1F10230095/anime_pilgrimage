from django.shortcuts import render, get_object_or_404, redirect
from .models import Spot, Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required

def home(request):
    spots = Spot.objects.all()
    return render(request, 'spots/home.html', {'spots': spots})

def spot_list(request):
    keyword = request.GET.get('q', '')
    spots = Spot.objects.filter(title__icontains=keyword)
    return render(request, 'spots/spot_list.html', {'spots': spots, 'keyword': keyword})

def spot_detail(request, pk):
    spot = get_object_or_404(Spot, pk=pk)
    return render(request, 'spot_detail.html', {'spot': spot})

def map_view(request):
    spots = Spot.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return render(request, 'spots/map.html', {'spots': spots})

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'spots/post_list.html', {'posts': posts})

def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # ログインユーザーを設定
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'spots/post_form.html', {'form': form})