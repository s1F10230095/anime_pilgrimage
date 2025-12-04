from django.contrib import admin
# ▼ 1. ここに新しく作った Title と UserTitle (あとPostなど) を追加します
from .models import Spot, Post, Comment, Title, UserTitle 

# Spotの一覧画面をカスタマイズする設定（順番を変えて有効化します）
class SpotAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "spot_type")
    search_fields = ("title", "location", "spot_type")
    list_filter = ("spot_type",)

# ▼ 2. 最後にまとめて登録します
# Spotに SpotAdmin を紐付けて登録
admin.site.register(Spot, SpotAdmin)

# 他のモデルも登録（これで管理画面に出るようになります）
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Title)      # 🏆 称号を作る場所
admin.site.register(UserTitle)  # 👤 獲得した称号を確認する場所