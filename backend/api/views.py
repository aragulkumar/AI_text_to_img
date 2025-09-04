import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

@api_view(['POST'])
def generate_image(request):
    prompt = request.data.get("prompt")
    headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
    payload = {"inputs": prompt}

    try:
        res = requests.post(
            "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
            headers=headers,
            json=payload
        )

        if res.status_code != 200:
            return Response({"error": res.text}, status=res.status_code)

        return Response(res.json())

    except Exception as e:
        return Response({"error": str(e)}, status=500)
