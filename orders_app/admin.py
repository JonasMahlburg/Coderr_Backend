from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'offer', 'ordered_detail', 'status', 'quantity', 'price_at_order', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('customer__username', 'offer__title', 'ordered_detail__title')
    ordering = ('-created_at',)
