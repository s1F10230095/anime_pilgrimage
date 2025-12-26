from django.shortcuts import render, get_object_or_404, redirect
from .models import Spot, Post, Title, UserTitle, Profile # Profileモデルをインポートに追加 (もし必要なら)
from .forms import PostForm, ProfileForm # ProfileFormをインポートに追加 (もし必要なら)
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .utils import calculate_distance
from openai import OpenAI
import json

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
            # カンマ(半角/全角)、スペース(全角)で分割できるようにする
            parts = [p.strip() for p in g.replace('、', ',').replace('　', ',').replace(' ', ',').split(',')]
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
    
    # ▼▼▼ 追加：訪問済み（称号持ち）チェック ▼▼▼
    has_visited = False
    if request.user.is_authenticated:
        # ログイン中のユーザーが、このスポットに関連する称号を持っているか確認
        has_visited = UserTitle.objects.filter(
            user=request.user, 
            title__related_spot=spot
        ).exists()
    
    return render(request, 'spots/spot_detail.html', {
        'spot': spot,
        'has_visited': has_visited  # テンプレートに結果を渡す
    })

@login_required
def post_create(request):
    # ▼▼▼ 追加：詳細画面から「spot_id」が送られてきたら受け取る ▼▼▼
    initial_data = {}
    spot_id = request.GET.get('spot_id')
    if spot_id:
        spot = get_object_or_404(Spot, pk=spot_id)
        initial_data['spot'] = spot  # フォームの初期値にセット

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        # ▼▼▼ 修正：初期値(initial)を渡してフォームを作る ▼▼▼
        form = PostForm(initial=initial_data)
        
    return render(request, 'spots/post_form.html', {'form': form})

@login_required
def toggle_favorite(request, spot_id):
    spot = get_object_or_404(Spot, pk=spot_id)
    
    # すでに登録済みなら解除、なければ登録
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
    # ProfileFormが未定義の場合、ここでエラーになる可能性があります
    # 必要に応じて、from .forms import ProfileForm を追加してください
    
    # ユーザーがProfileを持っている前提（models.pyのシグナルで作成済み）
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


@csrf_exempt # 本番ではCSRFトークンをJSで送るべきですが、まずは簡易実装
def check_location(request):
    """ 現在地を受け取って、近くの聖地の称号を付与するAPI """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            user_lat = float(data.get('latitude'))
            user_lon = float(data.get('longitude'))

            earned_titles = []

            # 全ての聖地と距離を比較（聖地が増えすぎたら将来的に改善が必要）
            spots = Spot.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

            for spot in spots:
                distance = calculate_distance(user_lat, user_lon, spot.latitude, spot.longitude)
                
                # 🎯 判定：250メートル以内なら
                if distance <= 250:
                    # そのスポットに関連する称号を探す
                    titles = Title.objects.filter(related_spot=spot)
                    
                    for title in titles:
                        # まだ持っていない場合のみ付与
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

# ==== あなたが Colab で使った設定 ====
OPENAI_API_KEY = "1H14XTSCsJnjwWCtHdFnbXdf1EG_lUbYsUcqfgJcTuud5ljDwR0uo2NJY3Urz8NW6eUtFp1zFQdqO6NLnncgdiQ"
OPENAI_API_BASE = "https://api.openai.iniad.org/api/v1"

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


def ai_travel(request):
    ai_response = None
    waypoints = []     # 地図描画用の座標リスト
    waypoints_json = "[]" # JavaScriptに渡すためのJSON文字列

    if request.method == "POST":
        user_input = request.POST.get("user_input")

        # 🎯 プロンプトの魔改造：JSON形式で座標を出力するように指示します
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
                # JSONモードを有効化（これで確実にJSONが返ってきます）
                response_format={"type": "json_object"} 
            )

            # AIの返答を辞書データに変換
            content = response.choices[0].message.content
            data = json.loads(content)
            
            ai_response = data.get("plan_text", "")
            waypoints = data.get("waypoints", [])
            waypoints_json = json.dumps(waypoints) # JS用に文字列化

        except Exception as e:
            ai_response = f"エラーが発生しました: {str(e)}"
            waypoints = []

    return render(request, "spots/ai_travel.html", {
        "ai_response": ai_response,
        "waypoints": waypoints,
        "waypoints_json": waypoints_json
    })
