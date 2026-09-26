from django.db import models

# Create your models here.
class ZohoToken(models.Model):
    user_identifier = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.user_identifier