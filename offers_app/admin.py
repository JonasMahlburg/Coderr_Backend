from django.contrib import admin
from .models import Offer, OfferDetail

class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 1

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'offer_type', 'created_at', 'updated_at')
    list_filter = ('offer_type', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [OfferDetailInline]

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer', 'price', 'revisions', 'delivery_time_in_days', 'offer_type')
    list_filter = ('offer_type',)
    search_fields = ('title', 'offer__title')
