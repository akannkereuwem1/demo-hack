from django.urls import path
from .views import ImageClassificationView, PricePredictionView

urlpatterns = [
    path('classify/', ImageClassificationView.as_view(), name='ai-classify'),
    path('predict-price/', PricePredictionView.as_view(), name='ai-predict'),
]
