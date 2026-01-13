from django.shortcuts import render, get_object_or_404, redirect
# ▼▼▼ Visit を追加しました ▼▼▼
from .models import Spot, Post, Comment, Title, UserTitle, Work, Visit
from accounts.models import Profile 
from django.contrib.auth.models import User
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

# --- 基本ビュー ---

def home(request):
    spots = Spot.objects.all()
    return render(request, 'spots/home.html', {'spots': spots})

def spot_list(request):
    selected_genre = request.GET.get('genre', '')

    raw_genres = Work.objects.values_list('genre', flat=True)
    genre_set = set()

    for g in raw_genres:
        if g:
            parts = [p.strip() for p in g.replace('、', ',').replace('　', ',').replace(' ', ',').split(',')]
            for p in parts:
                if p:
                    genre_set.add(p)

    genres = sorted(genre_set)

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

# --- 投稿関連 ---

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'spots/post_list.html', {'posts': posts})

@login_required
def post_create(request):
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
            if spot_id:
                 post.spot = get_object_or_404(Spot, pk=spot_id)
            post.save()
            return redirect('post_list')
    else:
        form = PostForm(initial=initial_data)
        
    return render(request, 'spots/post_form.html', {'form': form})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == "POST":
        post.delete()
    return redirect('post_list')

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

# --- 詳細・お気に入り ---

def spot_detail(request, pk):
    spot = get_object_or_404(Spot, pk=pk)

    # 訪問済み(スタンプあり)か判定
    has_visited = False
    if request.user.is_authenticated:
        has_visited = Visit.objects.filter(user=request.user, spot=spot).exists()

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

# --- プロフィール ---

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

def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    return render(request, 'spots/user_profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
    })

# --- 位置情報判定 (スタンプラリー機能) ---

@csrf_exempt 
def check_location(request):
    """ 現在地を受け取って、スタンプ(Visit)を押し、コンプリートなら称号を付与する """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            user_lat = float(data.get('latitude'))
            user_lon = float(data.get('longitude'))

            earned_titles = []
            spots = Spot.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

            for spot in spots:
                distance = calculate_distance(user_lat, user_lon, spot.latitude, spot.longitude)
                
                # 半径250m以内ならスタンプゲット
                if distance <= 250:
                    # 1. 訪問記録(スタンプ)を作成
                    # get_or_create なので、既にスタンプがあってもエラーにならず、重複もしない
                    visit_obj, created = Visit.objects.get_or_create(user=request.user, spot=spot)
                    
                    if created:
                        # 初めての訪問なら、ログに出すか何かしてもいいかも
                        pass

                    # 2. 個別の聖地称号があれば付与（もしあれば）
                    titles = Title.objects.filter(related_spot=spot)
                    for title in titles:
                        obj, t_created = UserTitle.objects.get_or_create(user=request.user, title=title)
                        if t_created:
                            earned_titles.append(title.name)

                    # 3. コンプリート判定（ここが新機能！）
                    if spot.work:
                        work = spot.work
                        # このアニメの聖地総数
                        all_spots_count = work.spots.count()
                        # ユーザーが訪れたこのアニメの聖地数
                        visited_count = Visit.objects.filter(user=request.user, spot__work=work).count()
                        
                        # 全て回っていたら
                        if visited_count >= all_spots_count:
                            # コンプリート称号（SpotがNULLでWorkが設定されている称号）を探す
                            comp_titles = Title.objects.filter(related_work=work, related_spot__isnull=True)
                            
                            for ct in comp_titles:
                                obj, c_created = UserTitle.objects.get_or_create(user=request.user, title=ct)
                                if c_created:
                                    earned_titles.append(f"【完全制覇】{ct.name}")

            if earned_titles:
                return JsonResponse({'status': 'success', 'new_titles': earned_titles})
            else:
                return JsonResponse({'status': 'no_change'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# --- AI旅行プラン ---

OPENAI_API_BASE = "https://api.openai.iniad.org/api/v1"

def ai_travel(request):
    ai_response = None
    waypoints = []
    waypoints_json = "[]"

    if request.method == "POST":
        user_input = request.POST.get("user_input")

        system_prompt = """
        あなたはアニメ聖地巡礼のプロ旅行プランナーです。
        ユーザーの要望に合わせて、具体的で最適な旅行プランを提案してください。
        
        【重要】出力は必ず以下のJSON形式のみにしてください。
        {
            "plan_text": "説明文...",
            "waypoints": [
                {"name": "場所名", "lat": 緯度, "lng": 経度},
                ...
            ]
        }
        """

        # ▼▼▼ 【ここを追加修正】 ▼▼▼
        # クライアントを初期化します。INIADのエンドポイントを指定します。
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), # 環境変数からキーを取得
            base_url=OPENAI_API_BASE,                 # INIADのアドレスを指定
        )
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

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
            # エラー内容を画面に出すようにしておくとデバッグしやすいです
            ai_response = f"エラーが発生しました: {str(e)}"
            waypoints = []

    return render(request, "spots/ai_travel.html", {
        "ai_response": ai_response,
        "waypoints": waypoints,
        "waypoints_json": waypoints_json
    })


# --- 作品詳細 (スタンプラリー台紙) ---

def work_detail(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    all_spots = work.spots.all()
    
    # テンプレートで「訪問済みか？」を判定しやすい形にデータを加工する
    spot_list = []
    for spot in all_spots:
        is_visited = False
        if request.user.is_authenticated:
            # Visitモデルに記録があるかチェック
            is_visited = Visit.objects.filter(user=request.user, spot=spot).exists()
        
        spot_list.append({
            'spot': spot,
            'is_visited': is_visited
        })

    # コンプリート済みか確認 (コンプリート称号を持っているかで判定)
    is_completed = False
    if request.user.is_authenticated:
        is_completed = UserTitle.objects.filter(
            user=request.user,
            title__related_work=work,
            title__related_spot__isnull=True
        ).exists()

    return render(request, 'spots/work_detail.html', {
        'work': work,
        'spot_list': spot_list,  # ここが重要！spotsそのものではなく、加工したリストを渡す
        'is_completed': is_completed,
    })