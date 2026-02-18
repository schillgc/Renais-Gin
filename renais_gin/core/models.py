"""
Database models for Renais Gin platform.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime
from io import BytesIO

import qrcode
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    """
    Custom User model for Renais Gin platform.
    """
    karma_score = models.FloatField(default=0.0)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    Extended user profile with engagement tracking and preferences.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    engagement_score = models.IntegerField(default=0)
    impact_history = models.JSONField(default=list)
    preferred_causes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-engagement_score']
        indexes = [
            models.Index(fields=['-engagement_score']),
        ]

    def __str__(self):
        return f"{self.user.username} Profile (Engagement: {self.engagement_score})"

    def update_engagement_score(self):
        """Update engagement score based on user activity"""
        from django.db.models import Count
        pledges_count = self.user.pledges.count()
        validations_count = self.user.validations_given.count()
        bottles_count = self.user.bottles.count()

        # Calculate engagement score
        self.engagement_score = (
                pledges_count * 10 +
                validations_count * 5 +
                bottles_count * 3
        )
        self.save()


class Bottle(models.Model):
    """
    Represents a physical Renais Gin bottle with unique ID and terroir data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bottle_id = models.CharField(max_length=100, unique=True, db_index=True)
    batch_id = models.CharField(max_length=100, db_index=True)
    production_date = models.DateField()
    terroir_region = models.CharField(max_length=100, default='Chablis')
    terroir_vintage = models.CharField(max_length=10, default='2022')
    registered = models.BooleanField(default=False, db_index=True)
    registered_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bottles'
    )
    registration_date = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    status = models.CharField(max_length=20, default='unregistered', choices=[
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('pledged', 'Pledged'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['bottle_id']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['-registration_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Bottle {self.bottle_id}"

    def generate_qr_code(self):
        """Generate QR code for the bottle"""
        bottle_data = {
            'bottle_id': self.bottle_id,
            'batch_id': self.batch_id,
            'production_date': self.production_date.isoformat(),
            'terroir_region': self.terroir_region,
            'terroir_vintage': self.terroir_vintage
        }

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5,
        )
        qr.add_data(json.dumps(bottle_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color='black', back_color='white')

        # Save to memory
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        # Save to ImageField
        filename = f'{self.bottle_id}_qr.png'
        self.qr_code.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )

    def save(self, *args, **kwargs):
        """Override save to generate QR code if needed"""
        if not self.qr_code and self.bottle_id:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def can_make_pledge(self):
        """Check if bottle can make a pledge"""
        return self.registered and self.status == 'registered' and not self.pledges.exists()

    @property
    def has_pledge(self):
        """Check if bottle has an associated pledge"""
        return self.pledges.exists()


class KarmaPledge(models.Model):
    """
    Represents a community karma pledge linked to a bottle.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Validation'),
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_id = models.CharField(max_length=100, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pledges')
    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE, related_name='pledges')
    pledge_text = models.TextField()
    impact_plan = models.TextField()
    impact_type = models.CharField(
        max_length=20,
        choices=IMPACT_CHOICES,
        default='other',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    sentiment_score = models.FloatField(null=True, blank=True)
    ai_validation_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['impact_type']),
            models.Index(fields=['user']),
        ]
        unique_together = [['user', 'bottle']]

    def __str__(self):
        return f"Pledge {self.submission_id} by {self.user.username}"

    def save(self, *args, **kwargs):
        """Generate submission ID if not exists"""
        if not self.submission_id:
            self.submission_id = hashlib.sha256(
                f"{self.user.id}{self.bottle.bottle_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
        super().save(*args, **kwargs)

    @property
    def approval_count(self):
        """Get number of approvals"""
        return self.validations.filter(approved=True).count()

    @property
    def rejection_count(self):
        """Get number of rejections"""
        return self.validations.filter(approved=False).count()

    @property
    def total_validations(self):
        """Get total number of validations"""
        return self.validations.count()


class PledgeValidation(models.Model):
    """
    Community validation for karma pledges.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pledge = models.ForeignKey(KarmaPledge, on_delete=models.CASCADE, related_name='validations')
    validator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='validations_given')
    approved = models.BooleanField()
    comments = models.TextField(blank=True)
    validator_ip = models.GenericIPAddressField(null=True, blank=True)
    validator_user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['pledge', 'validator']
        indexes = [
            models.Index(fields=['pledge']),
            models.Index(fields=['validator']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        action = "approved" if self.approved else "rejected"
        return f"Validation by {self.validator.username} - {action}"


class Rebate(models.Model):
    """
    Rebate associated with an approved pledge.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pledge = models.OneToOneField(KarmaPledge, on_delete=models.CASCADE, related_name='rebate')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Rebate ${self.amount} for {self.pledge.submission_id}"

    def mark_processing(self):
        """Mark rebate as processing"""
        self.status = 'processing'
        self.save()

    def mark_completed(self, transaction_id):
        """Mark rebate as completed"""
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.processed_date = timezone.now()
        self.save()

    def mark_failed(self):
        """Mark rebate as failed"""
        self.status = 'failed'
        self.save()


class CommunityCircle(models.Model):
    """
    Local community groups for coordinated impact.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='led_circles'
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='community_circles', blank=True)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    focus_areas = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.location}"

    def add_member(self, user):
        """Add a member to the circle"""
        self.members.add(user)
        self.save()

    def remove_member(self, user):
        """Remove a member from the circle"""
        self.members.remove(user)
        self.save()

    @property
    def member_count(self):
        """Get total number of members including leader"""
        return self.members.count() + 1  # +1 for leader

    @property
    def total_members(self):
        """Get total number of people in circle"""
        return self.member_count


class MovementMetrics(models.Model):
    """
    Global movement statistics and metrics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_pledges = models.IntegerField(default=0)
    total_rebates = models.IntegerField(default=0)
    community_size = models.IntegerField(default=0)
    impact_stories = models.IntegerField(default=0)
    global_reach = models.JSONField(default=dict)  # Country: count mapping
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Movement Metrics"

    def __str__(self):
        return f"Movement Metrics - {self.last_updated.strftime('%Y-%m-%d %H:%M')}"


def user_pdf_upload_path(instance, filename):
    """Generate upload path for user PDFs"""
    return os.path.join('pdfs', 'user_uploads', str(instance.user.id), filename)


def report_pdf_upload_path(instance, filename):
    """Generate upload path for generated reports"""
    date_path = timezone.now().strftime('%Y/%m')
    return os.path.join('pdfs', 'generated_reports', date_path, filename)


class UserPDFDocument(models.Model):
    """
    User-uploaded PDF documents for pledge verification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to=user_pdf_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @property
    def file_size(self):
        """Get file size in MB"""
        if self.pdf_file:
            return round(self.pdf_file.size / (1024 * 1024), 2)
        return 0


class GeneratedReport(models.Model):
    """
    System-generated PDF reports for impact tracking.
    """
    REPORT_TYPES = [
        ('impact', 'Impact Report'),
        ('karma', 'Karma Report'),
        ('community', 'Community Report'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to=report_pdf_upload_path)
    generated_at = models.DateTimeField(auto_now_add=True)
    related_pledge = models.ForeignKey(
        KarmaPledge,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['-generated_at']),
            models.Index(fields=['report_type']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"
