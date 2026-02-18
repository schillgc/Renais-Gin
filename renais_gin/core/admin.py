"""
Django admin configuration for Renais Gin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, UserProfile, Bottle, KarmaPledge, PledgeValidation, Rebate,
    CommunityCircle, MovementMetrics, GeneratedReport, UserPDFDocument
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'karma_score', 'country', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'country']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Renais Gin Profile', {
            'fields': ('karma_score', 'country'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Renais Gin Profile', {
            'fields': ('karma_score', 'country'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'engagement_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'engagement_score')
        }),
        ('Preferences', {
            'fields': ('preferred_causes', 'impact_history'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = [
        'bottle_id', 'batch_id', 'production_date', 'terroir_region',
        'registered', 'registered_to', 'status', 'registration_date'
    ]
    list_filter = ['registered', 'status', 'production_date', 'batch_id', 'terroir_region']
    search_fields = ['bottle_id', 'batch_id', 'registered_to__username']
    readonly_fields = ['registration_date', 'created_at']
    fieldsets = (
        ('Bottle Information', {
            'fields': ('bottle_id', 'batch_id', 'production_date')
        }),
        ('Terroir Data', {
            'fields': ('terroir_region', 'terroir_vintage')
        }),
        ('Registration', {
            'fields': ('registered', 'registered_to', 'registration_date', 'status')
        }),
        ('QR Code', {
            'fields': ('qr_code',),
            'classes': ('collapse',)
        }),
    )


@admin.register(KarmaPledge)
class KarmaPledgeAdmin(admin.ModelAdmin):
    list_display = [
        'submission_id', 'user', 'bottle', 'impact_type', 'status',
        'sentiment_score', 'created_at'
    ]
    list_filter = ['status', 'impact_type', 'created_at']
    search_fields = [
        'submission_id', 'user__username', 'bottle__bottle_id',
        'pledge_text', 'impact_plan'
    ]
    readonly_fields = ['submission_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Submission Info', {
            'fields': ('submission_id', 'user', 'bottle')
        }),
        ('Pledge Content', {
            'fields': ('pledge_text', 'impact_plan', 'impact_type')
        }),
        ('Validation', {
            'fields': ('status', 'sentiment_score', 'ai_validation_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_pledges', 'reject_pledges', 'mark_needs_review']

    def approve_pledges(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} pledges approved.')
    approve_pledges.short_description = "Approve selected pledges"

    def reject_pledges(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} pledges rejected.')
    reject_pledges.short_description = "Reject selected pledges"

    def mark_needs_review(self, request, queryset):
        updated = queryset.update(status='needs_review')
        self.message_user(request, f'{updated} pledges marked for review.')
    mark_needs_review.short_description = "Mark selected pledges for review"


@admin.register(PledgeValidation)
class PledgeValidationAdmin(admin.ModelAdmin):
    list_display = ['pledge', 'validator', 'approved', 'created_at']
    list_filter = ['approved', 'created_at']
    search_fields = ['pledge__submission_id', 'validator__username', 'comments']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Validation Info', {
            'fields': ('pledge', 'validator', 'approved')
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
        ('Technical Info', {
            'fields': ('validator_ip', 'validator_user_agent'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Rebate)
class RebateAdmin(admin.ModelAdmin):
    list_display = ['pledge', 'amount', 'status', 'processed_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['pledge__submission_id', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Rebate Info', {
            'fields': ('pledge', 'amount', 'status')
        }),
        ('Processing', {
            'fields': ('transaction_id', 'processed_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_processing', 'mark_completed', 'mark_failed']

    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} rebates marked as processing.')
    mark_processing.short_description = "Mark selected rebates as processing"

    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='completed', processed_date=timezone.now())
        self.message_user(request, f'{updated} rebates marked as completed.')
    mark_completed.short_description = "Mark selected rebates as completed"

    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} rebates marked as failed.')
    mark_failed.short_description = "Mark selected rebates as failed"


@admin.register(CommunityCircle)
class CommunityCircleAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'location', 'member_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'location', 'created_at']
    search_fields = ['name', 'leader__username', 'location', 'description']
    filter_horizontal = ['members']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Circle Info', {
            'fields': ('name', 'leader', 'location', 'is_active')
        }),
        ('Description', {
            'fields': ('description', 'focus_areas')
        }),
        ('Members', {
            'fields': ('members',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'


@admin.register(MovementMetrics)
class MovementMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'total_pledges', 'total_rebates', 'community_size',
        'impact_stories', 'last_updated'
    ]
    readonly_fields = [
        'total_pledges', 'total_rebates', 'community_size',
        'impact_stories', 'global_reach', 'last_updated'
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserPDFDocument)
class UserPDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'uploaded_at', 'is_verified', 'file_size']
    list_filter = ['is_verified', 'uploaded_at']
    search_fields = ['title', 'user__username', 'description']
    readonly_fields = ['uploaded_at', 'file_size']
    fieldsets = (
        ('Document Info', {
            'fields': ('user', 'title', 'description')
        }),
        ('File', {
            'fields': ('pdf_file', 'is_verified')
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'file_size'),
            'classes': ('collapse',)
        }),
    )
    actions = ['verify_documents', 'unverify_documents']

    def verify_documents(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} documents verified.')
    verify_documents.short_description = "Verify selected documents"

    def unverify_documents(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} documents unverified.')
    unverify_documents.short_description = "Unverify selected documents"

    def file_size(self, obj):
        return f"{obj.file_size} MB" if obj.file_size else "0 MB"
    file_size.short_description = 'File Size'


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_at']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['generated_at']
    fieldsets = (
        ('Report Info', {
            'fields': ('report_type', 'title', 'description', 'related_pledge')
        }),
        ('File', {
            'fields': ('pdf_file',)
        }),
        ('Metadata', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
