from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'karma_score', 'country', 'is_community_validator', 'date_joined')
    list_filter = ('is_community_validator', 'country', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = UserAdmin.fieldsets + (
        ('Renais Gin Profile', {
            'fields': (
                'karma_score', 'country', 'bio', 'avatar',
                'impact_story', 'is_community_validator',
                'preferred_causes', 'notification_preferences'
            )
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_pledges', 'approved_pledges', 'total_rebates')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
