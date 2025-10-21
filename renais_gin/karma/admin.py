from django.contrib import admin
from .models import KarmaPledge, KarmaValidation, KarmaRebate

@admin.register(KarmaPledge)
class KarmaPledgeAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'user', 'bottle', 'status', 'ai_confidence_score')

@admin.register(KarmaValidation)
class KarmaValidationAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'validator', 'approval', 'created_at')

@admin.register(KarmaRebate)
class KarmaRebateAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'user', 'amount', 'status')
