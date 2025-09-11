from django.urls import path
from .views import GenerateImageView, PromptHistoryView, health_check

urlpatterns = [
    path('generate/', GenerateImageView.as_view(), name='generate-image'),
    path('history/', PromptHistoryView.as_view(), name='prompt-history'),
    path('health/', health_check, name='health-check'),
]

