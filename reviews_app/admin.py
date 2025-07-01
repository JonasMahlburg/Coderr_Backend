from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'business_user',
        'reviewer',
        'rating',
        'display_short_description',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'rating',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'business_user__username', 
        'reviewer__username',      
        'description'             
    )

    ordering = ('-updated_at',)

    readonly_fields = (
        'created_at',
        'updated_at'
    )

    fieldsets = (
        (None, {
            'fields': ('business_user', 'reviewer', 'rating'),
            'description': 'Basic review information.'
        }),
        ('Review Content', { 
            'fields': ('description',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically recorded dates and times.'
        }),
    )

    def display_short_description(self, obj):
        """
        Displays a truncated version of the review description
        for better readability in the list view.
        """
        if obj.description:
            return obj.description[:75] + '...' if len(obj.description) > 75 else obj.description
        return "—" 
    display_short_description.short_description = 'Description'


    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Manage Customer Reviews' 
        return super().changelist_view(request, extra_context=extra_context)