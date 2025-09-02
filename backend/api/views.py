from django.shortcuts import render
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

@api_view(['POST'])

def generate_image(request):
    prompt =  request.data.get("prompt")
    headers = {"Authorization":f"Bearer {settings.HF_API_KEY}"}
    payload = {"input": prompt}
    response = response.post(
        "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
        headers=headers,
        json=payload
    )
    return Response(response.json())

# Create your views here.
