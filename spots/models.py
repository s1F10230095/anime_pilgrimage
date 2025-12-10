from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# 聖地巡礼スポットのモデル
class Spot(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    spot_type = models.CharField(max_length=50)
    image_url = models.URLField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title

# ユーザーの投稿（巡礼記録）モデル
class Post(models.Model):
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='posts', null=True, blank=True) 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
    
# ユーザープロフィールモデル（Userモデルと1対1で紐づく）
class Profile(models.Model):
    # 💥 修正: related_name='spots_profile' を設定
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spots_profile') 
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# 称号（アチーブメント）の定義モデル
class Title(models.Model):
    name = models.CharField(max_length=100, verbose_name="称号名")
    related_spot = models.ForeignKey(Spot, on_delete=models.CASCADE, verbose_name="対象スポット", related_name='titles')
    
    def __str__(self):
        return self.name
    
# ユーザーが獲得した称号のモデル（多対多の関係を管理）
class UserTitle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    obtained_at = models.DateTimeField(auto_now_add=True, verbose_name="獲得日時")

    class Meta:
        unique_together = ('user', 'title') # 同じ称号を二重取りしないようにする

    def __str__(self):
        return f"{self.user.username} - {self.title.name}"

# シグナル（ユーザー作成時に自動でProfileを作成・保存する）
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    # 🚨 シグナルも修正: related_name に合わせてアクセス方法を変更
    if hasattr(instance, 'spots_profile'):
        instance.spots_profile.save()