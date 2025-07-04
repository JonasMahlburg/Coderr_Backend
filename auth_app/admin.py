from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    Organizes display, filtering, searching, read-only fields, and fieldsets
    for better usability in the Django admin interface.
    """
    list_display = (
        'user',
        'type',
        'location',
        'tel',
        'created_at',
    )
    list_filter = (
        'type',
        'location',
        'created_at',
    )
    search_fields = (
        'user__username',
        'location',
        'tel',
    )
    readonly_fields = (
        'created_at',
    )
    fieldsets = (
        (None, { # This is the first, unnamed fieldset for core user profile details
            'fields': (
                'user',
                'type',
                'bio',
                'description',
                'file',
            )
        }),
        ('Additional Info', { # A named fieldset for supplementary information
            'fields': (
                'location',
                'tel',
                'working_hours',
                'created_at', # 'created_at' is read-only and appears here
            )
        }),
    )
