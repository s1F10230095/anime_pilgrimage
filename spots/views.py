from django.shortcuts import render, get_object_or_404, redirect
from .models import Spot, Post
from .forms import PostForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def home(request):
    spots = Spot.objects.all()
    return render(request, 'spots/home.html', {'spots': spots})

def spot_list(request):
    selected_genre = request.GET.get('genre', '')

    # --- 🔹 全スポットの spot_type からジャンルを抽出 ---
    raw_genres = Spot.objects.values_list('spot_type', flat=True)
    genre_set = set()

    # --- 🔹 カンマ・全角スペースなどで分割して整理 ---
    for g in raw_genres:
        if g:
            parts = [p.strip() for p in g.replace('、', ',').replace('　', ' ').split(',')]
            for p in parts:
                if p:
                    genre_set.add(p)

    # --- 🔹 ソートしてリストに変換 ---
    genres = sorted(genre_set)

    # --- 🔹 含む一致で絞り込み ---
    if selected_genre:
        spots = Spot.objects.filter(Q(spot_type__icontains=selected_genre))
    else:
        spots = Spot.objects.all()

    return render(request, 'spots/spot_list.html', {
        'spots': spots,
        'genres': genres,
        'selected_genre': selected_genre,
    })

def map_view(request):
    spots = Spot.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    return render(request, 'spots/map.html', {'spots': spots})

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'spots/post_list.html', {'posts': posts})

@login_required
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

def spot_detail(request, pk):
    spot = get_object_or_404(Spot, pk=pk)
    return render(request, 'spots/spot_detail.html', {'spot': spot})