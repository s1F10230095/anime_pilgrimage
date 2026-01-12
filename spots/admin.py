from django.contrib import admin
# ▼▼▼ Visit を追加しました ▼▼▼
from .models import Spot, Post, Comment, Title, UserTitle, Work, Visit


# --- Work（作品）管理画面 ---
class WorkAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "representative_location")
    search_fields = ("title", "genre", "representative_location")
    list_filter = ("genre",)


# --- Spot（聖地）管理画面 ---
class SpotAdmin(admin.ModelAdmin):
    list_display = ("work", "location")
    search_fields = ("work__title", "location")
    list_filter = ("work",)


# --- register ---
admin.site.register(Work, WorkAdmin)
admin.site.register(Spot, SpotAdmin)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Title)
admin.site.register(UserTitle)
admin.site.register(Visit)