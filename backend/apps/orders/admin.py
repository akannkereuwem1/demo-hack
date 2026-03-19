from django.contrib import admin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'farmer', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    search_fields = ['id', 'buyer__email', 'farmer__email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'unit_price']
    readonly_fields = ['id']
