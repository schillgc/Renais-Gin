from django.contrib import admin
from .models import UserProfile, Bottle, KarmaPledge, CommunityCircle, MovementMetrics, GeneratedReport, UserPDFDocument


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'karma_score', 'country')
    search_fields = ('user__username', 'user__email', 'country')


@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = ('bottle_id', 'batch_id', 'production_date', 'region_display', 'vintage_display', 'registered')
    list_filter = ('registered', 'production_date', 'batch_id')
    search_fields = ('bottle_id', 'batch_id', 'terroir_data')
    readonly_fields = ('terroir_data_prettified',)

    def region_display(self, obj):
        return obj.terroir_data.get('region', 'N/A')

    region_display.short_description = 'Region'

    def vintage_display(self, obj):
        return obj.terroir_data.get('vintage', 'N/A')

    vintage_display.short_description = 'Vintage'

    def terroir_data_prettified(self, obj):
        # Format the JSON data for better display in admin
        import json
        return json.dumps(obj.terroir_data, indent=2)

    terroir_data_prettified.short_description = 'Terroir Data (Formatted)'


@admin.register(KarmaPledge)
class KarmaPledgeAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'user', 'bottle', 'impact_type', 'status', 'approvals', 'timestamp')
    list_filter = ('status', 'impact_type', 'timestamp')
    search_fields = ('user__username', 'bottle__bottle_id', 'pledge_text')
    readonly_fields = ('submission_id', 'timestamp')


@admin.register(CommunityCircle)
class CommunityCircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'location', 'created_at')
    filter_horizontal = ('members',)
    search_fields = ('name', 'leader__username', 'location')


@admin.register(MovementMetrics)
class MovementMetricsAdmin(admin.ModelAdmin):
    list_display = ('total_pledges', 'total_rebates', 'community_size', 'impact_stories', 'last_updated')
    readonly_fields = ('total_pledges', 'total_rebates', 'community_size', 'impact_stories', 'global_reach',
                       'last_updated')

    def has_add_permission(self, request):
        return False


@admin.register(UserPDFDocument)
class UserPDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'uploaded_at', 'is_verified')
    list_filter = ('is_verified', 'uploaded_at')
    search_fields = ('title', 'user__username', 'description')
    readonly_fields = ('uploaded_at',)


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_at')
    list_filter = ('report_type', 'generated_at')
    search_fields = ('title', 'description')
    readonly_fields = ('generated_at',)
