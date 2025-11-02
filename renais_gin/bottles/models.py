from django.db import models
from django.conf import settings
from django.utils import timezone


class BottleBatch(models.Model):
    batch_id = models.CharField(max_length=100, unique=True)
    production_date = models.DateField()
    region = models.CharField(max_length=100)
    vintage = models.CharField(max_length=10)
    terroir_data = models.JSONField(default=dict)
    total_bottles = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batch {self.batch_id}"


class Bottle(models.Model):
    bottle_id = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(BottleBatch, on_delete=models.CASCADE, related_name='bottles')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    is_registered = models.BooleanField(default=False)
    registered_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='bottles')
    registration_date = models.DateTimeField(null=True, blank=True)
    # Add pledge-related fields
    pledge_submitted = models.BooleanField(default=False)
    pledge_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bottle_id

    def save(self, *args, **kwargs):
        if self.is_registered and not self.registration_date:
            self.registration_date = timezone.now()
        super().save(*args, **kwargs)


class BottleScan(models.Model):
    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scan_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"Scan of {self.bottle.bottle_id} by {self.scanned_by.username}"
