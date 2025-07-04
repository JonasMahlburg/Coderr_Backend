from django.contrib import admin
from .models import Offer, OfferDetail

class OfferDetailInline(admin.TabularInline):
    """
    Allows inline editing of OfferDetail instances on the Offer admin page.
    Uses TabularInline for a compact table format.
    """
    model = OfferDetail
    extra = 1
    fields = (
        'title',
        'description',
        'price',
        'revisions',
        'delivery_time_in_days',
        'offer_type'
    )

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Offer model.
    Organizes display, filtering, search, and inlines for improved usability.
    """
    list_display = (
        'title',
        'user',
        'offer_type',
        'display_detail_count',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'offer_type',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'title',
        'description',
        'user__username'
    )

    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'offer_type'),
            'description': 'Main information about the offer.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically recorded timestamps.'
        }),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

    inlines = [OfferDetailInline]

    def display_detail_count(self, obj):
        """
        Calculates and displays the number of OfferDetails related to this offer.
        """
        return obj.details.count()
    display_detail_count.short_description = 'Details'

    def changelist_view(self, request, extra_context=None):
        """
        Customizes the title of the changelist view.
        """
        extra_context = extra_context or {}
        extra_context['title'] = 'Manage Offers'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """
    Admin configuration for the OfferDetail model.
    Optimized for display and search. Note: often managed via OfferInline.
    """
    list_display = (
        'title',
        'offer',
        'price',
        'revisions',
        'delivery_time_in_days',
        'offer_type',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'offer_type',
        'price',
        'revisions',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'title',
        'description',
        'offer__title'
    )

    ordering = ('offer__title', 'title')

    fieldsets = (
        (None, {
            'fields': ('offer', 'title', 'description', 'offer_type'),
            'description': 'Core information for this specific offer detail.'
        }),
        ('Pricing & Delivery', {
            'fields': ('price', 'revisions', 'delivery_time_in_days'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Record of creation and last update.'
        }),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

    def changelist_view(self, request, extra_context=None):
        """
        Customizes the title of the changelist view.
        """
        extra_context = extra_context or {}
        extra_context['title'] = 'Manage Offer Details'
        return super().changelist_view(request, extra_context=extra_context)