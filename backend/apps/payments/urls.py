from django.urls import path
from .views import PaymentProcessView, PaymentWebhookView

urlpatterns = [
    path('process/', PaymentProcessView.as_view(), name='payment-process'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
]
