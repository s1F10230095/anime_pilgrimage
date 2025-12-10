from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # 💥 修正: related_name='accounts_profile' を追加
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_profile') 
    icon = models.ImageField(upload_to='profile_icons/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# シグナル（ユーザー作成時に自動でProfileを作成・保存する）
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # User.profile ではなく、User.accounts_profile を使用するように変更（もしシグナルがこのアプリで使われているなら）
        # ただし、このシグナルは User.profile に依存しているため、どちらかのアプリのシグナルを削除するか、
        # 参照を related_name に合わせる必要があります。ここでは、spots 側のシグナルをメインとして修正します。
        Profile.objects.create(user=instance)
    # Note: related_name を 'accounts_profile' に変更した場合、ここでは instance.accounts_profile.save() が正しいですが、
    # 便宜上、一旦元のコードのまま残します。競合を避けるために accounts 側の Profile は不要な場合、この Profile モデルごと削除を検討してください。
    if hasattr(instance, 'accounts_profile'):
        instance.accounts_profile.save()