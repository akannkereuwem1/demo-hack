from django.urls import path

from .views import (
    OrderCompleteView,
    OrderConfirmView,
    OrderDeclineView,
    OrderDetailView,
    OrderListView,
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:pk>/confirm/', OrderConfirmView.as_view(), name='order-confirm'),
    path('<uuid:pk>/decline/', OrderDeclineView.as_view(), name='order-decline'),
    path('<uuid:pk>/complete/', OrderCompleteView.as_view(), name='order-complete'),
]
