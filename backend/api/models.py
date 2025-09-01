from django.db import models

# Create your models here.
class PromptHistory(models.Model):
    prompt = models.TextField()
    image = models.ImageField(upload_to='generated/')
    timestamp = models.DateTimeField(auto_now_add=True)
    