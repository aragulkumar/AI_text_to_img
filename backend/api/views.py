import os
import time
import requests
import base64
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PromptHistory
from .serializers import ImageGenerationSerializer, PromptHistorySerializer


class LocalImageGenerator:
    def __init__(self):
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            self.torch = torch
            self.StableDiffusionPipeline = StableDiffusionPipeline
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.pipe = None
            self._load_model()
        except ImportError:
            raise ImportError("Diffusers library not installed. Run: pip install diffusers torch")
    
    def _load_model(self):
        if not self.pipe:
            model_path = settings.LOCAL_MODEL_PATH or "runwayml/stable-diffusion-v1-5"
            self.pipe = self.StableDiffusionPipeline.from_pretrained(
                model_path,
                torch_dtype=self.torch.float16 if self.device == "cuda" else self.torch.float32
            )
            self.pipe = self.pipe.to(self.device)
    
    def generate_image(self, prompt, style="realistic", width=512, height=512):
        full_prompt = f"{prompt}, {style} style"
        
        try:
            image = self.pipe(
                prompt=full_prompt,
                width=width,
                height=height,
                num_inference_steps=20,
                guidance_scale=7.5
            ).images[0]
            
            # Convert PIL image to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
            
        except Exception as e:
            raise ValueError(f"Local generation error: {str(e)}")

# Main API Views
class GenerateImageView(APIView):
    permission_classes = [AllowAny]  # Remove for production
    
    def post(self, request):
        serializer = ImageGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = serializer.validated_data['prompt']
        style = serializer.validated_data.get('style', 'realistic')
        width = serializer.validated_data.get('width', 512)
        height = serializer.validated_data.get('height', 512)
        
        start_time = time.time()
        
        try:
            # Choose generation method
            if settings.USE_LOCAL_MODEL:
                generator = LocalImageGenerator()
                image_bytes = generator.generate_image(prompt, style, width, height)
                model_used = "local-stable-diffusion"
            else:
                generator = HuggingFaceImageGenerator()
                image_bytes = generator.generate_image(prompt, style)
                model_used = "huggingface-api"
            
            generation_time = time.time() - start_time
            
            # Create PIL Image and save
            image = Image.open(BytesIO(image_bytes))
            image_file = BytesIO()
            image.save(image_file, format='PNG')
            image_file.seek(0)
            
            # Save to database
            prompt_history = PromptHistory(
                user=request.user if request.user.is_authenticated else None,
                prompt=prompt,
                style=style,
                generation_time=generation_time,
                model_used=model_used
            )
            
            # Save image file
            filename = f"generated_{int(time.time())}.png"
            prompt_history.image.save(filename, ContentFile(image_file.getvalue()))
            prompt_history.save()
            
            # Return response
            serializer = PromptHistorySerializer(prompt_history)
            return Response({
                'success': True,
                'data': serializer.data,
                'generation_time': generation_time,
                'model_used': model_used
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'troubleshooting': {
                    'hugging_face_issues': [
                        'Check if HUGGING_FACE_API_KEY is set in environment',
                        'Verify API key is valid and has correct permissions',
                        'Try a different model if current one is unavailable'
                    ],
                    'local_model_issues': [
                        'Install required packages: pip install diffusers torch',
                        'Ensure adequate GPU memory or use CPU',
                        'Check if model path is correct'
                    ]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PromptHistoryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            history = PromptHistory.objects.filter(user=request.user)
        else:
            # Return recent public generations for demo
            history = PromptHistory.objects.filter(user__isnull=True)[:10]
        
        serializer = PromptHistorySerializer(history, many=True)
        return Response(serializer.data)

# Health check endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'hugging_face_configured': bool(settings.HUGGING_FACE_API_KEY),
        'local_model_enabled': settings.USE_LOCAL_MODEL,
        'available_endpoints': [
            '/api/generate/',
            '/api/history/',
            '/api/health/'
        ]
    })