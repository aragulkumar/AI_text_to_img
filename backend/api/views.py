import requests
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

# 👇 Add this constant at the top of the file
MODEL_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-4"

@api_view(['POST'])
def generate_image(request):
    prompt = request.data.get("prompt")
    headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
    payload = {"inputs": prompt}

    try:
        res = requests.post(
            MODEL_URL,          # 👈 use the constant here
            headers=headers,
            json=payload,
            timeout=60
        )

        if res.status_code != 200:
            return Response({"error": res.text}, status=res.status_code)

        image_bytes = res.content
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        return Response({"image": image_base64})

    except requests.exceptions.Timeout:
        return Response({"error": "Hugging Face request timed out"}, status=504)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
