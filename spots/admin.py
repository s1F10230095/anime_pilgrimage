from django.contrib import admin
from .models import Spot

admin.site.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "spot_type")
    search_fields = ("title", "location", "spot_type")
    list_filter = ("spot_type",)

