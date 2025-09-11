from rest_framework import serializers
from .models import PromptHistory

class PromptHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptHistory
        fields = ['id', 'prompt', 'style', 'image', 'image_url', 'timestamp', 'generation_time', 'model_used']
        read_only_fields = ['id', 'timestamp', 'generation_time', 'model_used']

class ImageGenerationSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)
    style = serializers.CharField(max_length=100, default='realistic')
    width = serializers.IntegerField(default=512, min_value=256, max_value=1024)
    height = serializers.IntegerField(default=512, min_value=256, max_value=1024)
    num_inference_steps = serializers.IntegerField(default=20, min_value=1, max_value=100)