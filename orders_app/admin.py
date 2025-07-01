from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'offer',
        'ordered_detail',
        'status',
        'quantity',
        'price_at_order',
        'display_total_price',
        'updated_at'
    )

    list_filter = (
        'status',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'customer__username',     
        'offer__title',      
        'ordered_detail__title'   
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
        'updated_at',
        'price_at_order',       
        'display_total_price'   
    )

    fieldsets = (
        (None, { 
            'fields': ('customer', 'offer', 'ordered_detail'),
            'description': 'Core details about the customer and the ordered item.'
        }),
        ('Pricing & Quantity', {
            'fields': ('quantity', 'price_at_order', 'display_total_price'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Timestamps', { 
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically recorded dates and times for the order.'
        }),
    )

    def display_total_price(self, obj):
        """
        Calculates and displays the total price for the order (quantity * price_at_order).
        """
        return f"{obj.quantity * obj.price_at_order:.2f} €"
    display_total_price.short_description = 'Total Price'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Manage Customer Orders'
        return super().changelist_view(request, extra_context=extra_context)
