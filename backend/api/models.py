from django.db import models
from django.contrib.auth.models import User
import uuid

class PromptHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    style = models.CharField(max_length=100, default='realistic')
    image = models.ImageField(upload_to='generated/')
    image_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    generation_time = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=100, default='stable-diffusion')
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.prompt[:50]}... - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    