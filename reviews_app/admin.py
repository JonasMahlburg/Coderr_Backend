"""Admin configuration for the Review model, providing a customized interface for managing customer reviews."""

from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface definition for the Review model.

    Configures list display, filtering, search, ordering, readonly fields,
    and fieldsets to facilitate efficient management of customer reviews.
    """

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
        """
        Customize the changelist view to include a custom page title.

        Args:
            request: The HTTP request object.
            extra_context (dict, optional): Additional context variables for the template.

        Returns:
            HttpResponse: The response object for the changelist view.
        """
        extra_context = extra_context or {}
        extra_context['title'] = 'Manage Customer Reviews' 
        return super().changelist_view(request, extra_context=extra_context)