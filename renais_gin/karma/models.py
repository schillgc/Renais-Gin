from django.db import models
from django.conf import settings


class KarmaPledge(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_NEEDS_REVIEW = 'needs_review'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Validation'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_NEEDS_REVIEW, 'Needs Review'),
    ]

    IMPACT_ENVIRONMENTAL = 'environmental'
    IMPACT_COMMUNITY = 'community'
    IMPACT_EDUCATION = 'education'
    IMPACT_OTHER = 'other'

    IMPACT_CHOICES = [
        (IMPACT_ENVIRONMENTAL, 'Environmental'),
        (IMPACT_COMMUNITY, 'Community'),
        (IMPACT_EDUCATION, 'Education'),
        (IMPACT_OTHER, 'Other'),
    ]

    submission_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pledges')
    bottle = models.ForeignKey('bottles.Bottle', on_delete=models.CASCADE, related_name='pledges')
    pledge_text = models.TextField()
    impact_plan = models.TextField()
    impact_type = models.CharField(max_length=20, choices=IMPACT_CHOICES, default=IMPACT_OTHER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    ai_confidence_score = models.FloatField(null=True, blank=True)
    approvals = models.IntegerField(default=0)
    rejections = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pledge {self.submission_id} by {self.user.username}"


class KarmaValidation(models.Model):
    pledge = models.ForeignKey(KarmaPledge, on_delete=models.CASCADE, related_name='validations')
    validator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='validations')
    approval = models.BooleanField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['pledge', 'validator']


class KarmaRebate(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSED = 'processed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_FAILED, 'Failed'),
    ]

    pledge = models.OneToOneField(KarmaPledge, on_delete=models.CASCADE, related_name='rebate')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rebates')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    processed_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rebate for {self.pledge.submission_id}"
