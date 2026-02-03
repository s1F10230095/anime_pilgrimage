from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# アニメ作品モデル（追加）
class Work(models.Model):
    title = models.CharField(max_length=100, verbose_name="作品名")
    description = models.TextField(blank=True, verbose_name="作品説明")
    genre = models.CharField(max_length=100, blank=True, verbose_name="ジャンル")
    image_url = models.URLField(blank=True, verbose_name="作品画像URL")
    representative_location = models.CharField(max_length=100, blank=True, verbose_name="代表の聖地（場所）")

    def __str__(self):
        return self.title

# 聖地巡礼スポットのモデル
class Spot(models.Model):
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name='spots',
        verbose_name="作品",
        null=True,
        blank=True
    )
    location = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='favorite_spots', 
        blank=True, 
        verbose_name="お気に入り登録したユーザー"
    )

    def __str__(self):
        if self.work_id:
            return f"{self.work.title} - {self.location}"
        return self.location

# ユーザーの投稿（巡礼記録）モデル
class Post(models.Model):
    spot = models.ForeignKey(
        'Spot',  # Spotモデルが同じファイルの下にある場合は文字列で指定
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
        verbose_name=_("聖地（ハッシュタグ）")  # ラベルを翻訳対象に
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 2. verbose_name を追加し、_("文字列") で囲む
    text = models.TextField(verbose_name=_("本文"))
    image = models.ImageField(
        _("画像"), # 第一引数に書くことでも verbose_name と同様に機能します
        upload_to='post_images/', 
        blank=True, 
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        blank=True
    )

    def __str__(self):
        return f"{self.author.username} - {self.spot.title if self.spot else 'No Spot'}"

# 投稿へのコメントモデル
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"
    

# 称号（アチーブメント）の定義モデル
class Title(models.Model):
    name = models.CharField(max_length=100, verbose_name="称号名")
    related_work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        verbose_name="対象作品",
        related_name='titles'
    )

    related_spot = models.ForeignKey(
        Spot,
        on_delete=models.CASCADE,
        verbose_name="対象聖地",
        null=True,   # 空欄OK（コンプリート称号用）
        blank=True,  # フォームで空欄OK
        related_name='titles'
    )

    def __str__(self):
        return f"{self.name}（{self.related_work.title}）"
    
# ユーザーが獲得した称号のモデル（多対多の関係を管理）
class UserTitle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    obtained_at = models.DateTimeField(auto_now_add=True, verbose_name="獲得日時")

    class Meta:
        unique_together = ('user', 'title') # 同じ称号を二重取りしないようにする

    def __str__(self):
        return f"{self.user.username} - {self.title.name}"
    
# ユーザーが聖地を訪れた記録（スタンプ）モデル
class Visit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='visits'
    )
    spot = models.ForeignKey(
        Spot, 
        on_delete=models.CASCADE, 
        related_name='visits'
    )
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 同じ場所に何度もスタンプは押さない（1ユーザー1聖地につき1回まで）
        unique_together = ('user', 'spot')

    def __str__(self):
        return f"{self.user.username} visited {self.spot.location}"