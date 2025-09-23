from django.db import models

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
