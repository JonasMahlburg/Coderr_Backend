from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'location', 'tel', 'created_at')
    list_filter = ('type', 'location', 'created_at')
    search_fields = ('user__username', 'location', 'tel')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'type', 'bio', 'description', 'file')
        }),
        ('Additional Info', {
            'fields': ('location', 'tel', 'working_hours', 'created_at')
        }),
    )
