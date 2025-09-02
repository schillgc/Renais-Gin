import os
import hashlib
import json
from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO
from PIL import Image
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    karma_score = models.FloatField(default=0.0)
    country = models.CharField(max_length=100, blank=True)
    impact_history = models.JSONField(default=list)
    preferences = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username} Profile"


class Bottle(models.Model):
    bottle_id = models.CharField(max_length=100, unique=True)
    batch_id = models.CharField(max_length=100)
    production_date = models.DateField()
    terroir_data = models.JSONField(default=dict)  # This stores the terroir information
    registered = models.BooleanField(default=False)
    registered_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    registration_date = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def __str__(self):
        return f"Bottle {self.bottle_id}"

    def generate_qr_code(self):
        bottle_data = {
            'bottle_id': self.bottle_id,
            'batch_id': self.batch_id,
            'production_date': self.production_date.isoformat(),
            'terroir_data': self.terroir_data
        }

        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(bottle_data))
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Save to memory
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        # Save to ImageField
        self.qr_code.save(
            f'{self.bottle_id}.png',
            ContentFile(buffer.getvalue()),
            save=False
        )

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bottle {self.bottle_id}"


class KarmaPledge(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('needs_review', 'Needs Review'),
    ]

    IMPACT_CHOICES = [
        ('environmental', 'Environmental'),
        ('community', 'Community'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    submission_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    pledge_text = models.TextField()
    impact_plan = models.TextField()
    impact_type = models.CharField(max_length=20, choices=IMPACT_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approvals = models.IntegerField(default=0)
    validations = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)
    rebate_processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.submission_id:
            self.submission_id = hashlib.sha256(
                f"{self.user.id}{self.bottle.bottle_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pledge {self.submission_id} by {self.user.username}"


class CommunityCircle(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_circles')
    members = models.ManyToManyField(User, related_name='community_circles')
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


class MovementMetrics(models.Model):
    total_pledges = models.IntegerField(default=0)
    total_rebates = models.IntegerField(default=0)
    community_size = models.IntegerField(default=0)
    impact_stories = models.IntegerField(default=0)
    global_reach = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Movement Metrics"

    def __str__(self):
        return f"Movement Metrics - {self.last_updated}"


def user_pdf_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/pdfs/user_uploads/<user_id>/<filename>
    return os.path.join('pdfs', 'user_uploads', str(instance.user.id), filename)


def report_pdf_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/pdfs/generated_reports/<year>/<month>/<filename>
    date_path = timezone.now().strftime('%Y/%m')
    return os.path.join('pdfs', 'generated_reports', date_path, filename)


class UserPDFDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to=user_pdf_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class GeneratedReport(models.Model):
    REPORT_TYPES = [
        ('impact', 'Impact Report'),
        ('karma', 'Karma Report'),
        ('community', 'Community Report'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to=report_pdf_upload_path)
    generated_at = models.DateTimeField(auto_now_add=True)
    related_pledge = models.ForeignKey('KarmaPledge', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"
