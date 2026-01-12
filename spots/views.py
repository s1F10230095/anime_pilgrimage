from django.shortcuts import render, get_object_or_404, redirect
# ▼▼▼ モデルのインポートを統合 (Workはitoから、Commentはmainから) ▼▼▼
from .models import Spot, Post, Comment, Title, UserTitle, Work
# Profileは main の構成(accountsアプリ)を正とします
from accounts.models import Profile 
from django.contrib.auth.models import User
# フォームのインポートを統合
from .forms import PostForm
from accounts.forms import ProfileForm

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import calculate_distance
from openai import OpenAI
import json
import os 

def home(request):
    spots = Spot.objects.all()
    return render(request, 'spots/home.html', {'spots': spots})

def spot_list(request):
    selected_genre = request.GET.get('genre', '')

    # Work.genre からジャンル一覧を作る（空は除外）
    raw_genres = Work.objects.values_list('genre', flat=True)
    genre_set = set()

    for g in raw_genres:
        if g:
            # 「SF, 日常」みたいに複数入れても分解できるようにする
            parts = [p.strip() for p in g.replace('、', ',').replace('　', ',').replace(' ', ',').split(',')]
            for p in parts:
                if p:
                    genre_set.add(p)

    genres = sorted(genre_set)

    # ジャンルで絞り込み
    if selected_genre:
        works = Work.objects.filter(genre__icontains=selected_genre)
    else:
        works = Work.objects.all()

    return render(request, 'spots/spot_list.html', {
        'works': works,
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
    # 詳細画面から「spot_id」が送られてきたら受け取る
    initial_data = {}
    spot_id = request.GET.get('spot_id')
    if spot_id:
        spot = get_object_or_404(Spot, pk=spot_id)
        initial_data['spot'] = spot 

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # URLから聖地が指定されていたら強制的に紐付ける
            if spot_id:
                 post.spot = get_object_or_404(Spot, pk=spot_id)
            post.save()
            return redirect('post_list')
    else:
        form = PostForm(initial=initial_data)
        
    return render(request, 'spots/post_form.html', {'form': form})

def spot_detail(request, pk):
    spot = get_object_or_404(Spot, pk=pk)

    has_visited = False
    if request.user.is_authenticated:
        # Spot → 紐づく Work で称号を判定する
        if spot.work:
            has_visited = UserTitle.objects.filter(
                user=request.user,
                title__related_work=spot.work
            ).exists()

    return render(request, 'spots/spot_detail.html', {
        'spot': spot,
        'has_visited': has_visited
    })

@login_required
def toggle_favorite(request, spot_id):
    spot = get_object_or_404(Spot, pk=spot_id)
    
    if spot.favorites.filter(id=request.user.id).exists():
        spot.favorites.remove(request.user)
        liked = False
    else:
        spot.favorites.add(request.user)
        liked = True
        
    return JsonResponse({'liked': liked, 'count': spot.favorites.count()})


# --- 統合された関数群 ---

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'spots/profile_form.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'spots/profile_view.html', {'profile': profile})


@csrf_exempt 
def check_location(request):
    """ 現在地を受け取って、近くの聖地の称号を付与するAPI """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            user_lat = float(data.get('latitude'))
            user_lon = float(data.get('longitude'))

            earned_titles = []
            spots = Spot.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

            for spot in spots:
                distance = calculate_distance(user_lat, user_lon, spot.latitude, spot.longitude)
                
                if distance <= 250:
                    titles = Title.objects.filter(related_spot=spot)
                    for title in titles:
                        obj, created = UserTitle.objects.get_or_create(user=request.user, title=title)
                        if created:
                            earned_titles.append(title.name)

            if earned_titles:
                return JsonResponse({'status': 'success', 'new_titles': earned_titles})
            else:
                return JsonResponse({'status': 'no_change'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# 環境変数設定 (変更なし)
OPENAI_API_BASE = "https://api.openai.iniad.org/api/v1"
# client = OpenAI(...) 

def ai_travel(request):
    ai_response = None
    waypoints = []
    waypoints_json = "[]"

    if request.method == "POST":
        user_input = request.POST.get("user_input")

        system_prompt = """
        あなたはアニメ聖地巡礼のプロ旅行プランナーです。
        ユーザーの要望に合わせて、具体的で最適な旅行プランを提案してください。
        
        【重要】出力は必ず以下のJSON形式のみにしてください。冒頭の挨拶や余計な会話は不要です。
        {
            "plan_text": "ここに旅行プランの詳細な説明文（マークダウン形式推奨）を書く。時間は具体的に。",
            "waypoints": [
                {"name": "出発地点の場所名", "lat": 緯度(数値), "lng": 経度(数値)},
                {"name": "1つ目の経由地", "lat": 緯度, "lng": 経度},
                {"name": "...", "lat": ..., "lng": ...},
                {"name": "ゴール地点", "lat": ..., "lng": ...}
            ]
        }
        ※ 座標（lat, lng）はあなたの知識から可能な限り正確な数値を推測して入れてください。
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                response_format={"type": "json_object"} 
            )

            content = response.choices[0].message.content
            data = json.loads(content)
            
            ai_response = data.get("plan_text", "")
            waypoints = data.get("waypoints", [])
            waypoints_json = json.dumps(waypoints)

        except Exception as e:
            ai_response = f"エラーが発生しました: {str(e)}"
            waypoints = []

    return render(request, "spots/ai_travel.html", {
        "ai_response": ai_response,
        "waypoints": waypoints,
        "waypoints_json": waypoints_json
    })

# ▼▼▼ ito ブランチ由来の機能 (作品詳細) ▼▼▼
def work_detail(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    spots = work.spots.all()

    return render(request, 'spots/work_detail.html', {
        'work': work,
        'spots': spots,
    })

# ▼▼▼ main ブランチ由来の機能 (SNS/ユーザープロフィール) ▼▼▼
def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    return render(request, 'spots/user_profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
    })

@login_required
def toggle_post_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('post_list')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )

    return redirect('post_list')

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('post_list')

    if request.method == "POST":
        post.delete()

    return redirect('post_list')