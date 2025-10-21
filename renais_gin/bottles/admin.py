from django.contrib import admin
from .models import BottleBatch, Bottle, BottleScan

@admin.register(BottleBatch)
class BottleBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_id', 'production_date', 'region', 'vintage', 'total_bottles')

@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = ('bottle_id', 'batch', 'is_registered', 'registered_to')

@admin.register(BottleScan)
class BottleScanAdmin(admin.ModelAdmin):
    list_display = ('bottle', 'scanned_by', 'scan_date')
