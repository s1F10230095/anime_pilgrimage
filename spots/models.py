from django.db import models
from django.contrib.auth.models import User

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

class Post(models.Model):
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)  # ← ここを修正
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.spot.title if self.spot else 'No Spot'}"
