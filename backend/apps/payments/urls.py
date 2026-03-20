from django.urls import path

from .views import PaymentInitiateView, PaymentVerifyView, PaymentWebhookView

urlpatterns = [
    path('initiate/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('verify/', PaymentVerifyView.as_view(), name='payment-verify'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
]
