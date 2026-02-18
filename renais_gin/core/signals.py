"""
Signal handlers for Renais Gin core application.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone

from .models import (
    UserProfile, Bottle, KarmaPledge, PledgeValidation,
    Rebate, CommunityCircle
)
from .tasks import (
    send_pledge_status_notification, send_rebate_processed_notification,
    update_movement_metrics, update_user_engagement_scores
)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile when a new user is created.
    """
    if created:
        UserProfile.objects.create(user=instance)
        print(f"✅ Created user profile for {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save user profile when user is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=KarmaPledge)
def handle_pledge_status_change(sender, instance, created, **kwargs):
    """
    Handle actions when pledge status changes.
    """
    if not created:
        # Check if status changed
        if instance.tracker.has_changed('status'):
            print(f"🔄 Pledge {instance.submission_id} status changed to {instance.status}")

            # Send notification for status changes
            if instance.status in ['approved', 'rejected']:
                send_pledge_status_notification.delay(instance.id)

            # Update movement metrics
            update_movement_metrics.delay()


@receiver(post_save, sender=PledgeValidation)
def handle_new_validation(sender, instance, created, **kwargs):
    """
    Handle new pledge validations.
    """
    if created:
        print(f"✅ New validation for pledge {instance.pledge.submission_id}")

        # Update user engagement scores for validator
        update_user_engagement_scores.delay()

        # Update movement metrics
        update_movement_metrics.delay()


@receiver(post_save, sender=Rebate)
def handle_rebate_status_change(sender, instance, created, **kwargs):
    """
    Handle rebate status changes.
    """
    if not created and instance.tracker.has_changed('status'):
        print(f"💰 Rebate status changed to {instance.status} for pledge {instance.pledge.submission_id}")

        # Send notification when rebate is completed
        if instance.status == 'completed':
            send_rebate_processed_notification.delay(instance.id)

        # Update movement metrics
        update_movement_metrics.delay()


@receiver(post_save, sender=Bottle)
def handle_bottle_registration(sender, instance, created, **kwargs):
    """
    Handle bottle registration.
    """
    if not created and instance.tracker.has_changed('registered'):
        if instance.registered:
            print(f"🍾 Bottle {instance.bottle_id} registered to {instance.registered_to}")

            # Update user engagement score
            if instance.registered_to:
                update_user_engagement_scores.delay()

            # Update movement metrics
            update_movement_metrics.delay()


@receiver(post_save, sender=CommunityCircle)
def handle_community_circle_activity(sender, instance, created, **kwargs):
    """
    Handle community circle creation and updates.
    """
    if created:
        print(f"👥 New community circle created: {instance.name}")

    # Update movement metrics for circle activity
    update_movement_metrics.delay()


@receiver(post_delete, sender=KarmaPledge)
def handle_pledge_deletion(sender, instance, **kwargs):
    """
    Handle pledge deletion.
    """
    print(f"🗑️ Pledge {instance.submission_id} deleted")
    update_movement_metrics.delay()


@receiver(post_delete, sender=Bottle)
def handle_bottle_deletion(sender, instance, **kwargs):
    """
    Handle bottle deletion.
    """
    print(f"🗑️ Bottle {instance.bottle_id} deleted")
    update_movement_metrics.delay()


# Field tracking for detecting changes
def init_model_tracker(sender, **kwargs):
    """
    Initialize field tracker for detecting changes.
    """
    from model_utils import FieldTracker
    if hasattr(sender, 'tracker'):
        sender.tracker = FieldTracker(sender)


# Connect field tracker to models
models_with_tracking = [KarmaPledge, Rebate, Bottle]
for model in models_with_tracking:
    pre_save.connect(init_model_tracker, sender=model)


# Performance monitoring signals
@receiver(pre_save)
def log_model_save(sender, instance, **kwargs):
    """
    Log model save operations for performance monitoring.
    """
    if not sender._meta.app_label == 'contenttypes':  # Avoid logging internal models
        print(f"💾 Saving {sender.__name__}: {instance}")


@receiver(post_save)
def log_model_saved(sender, instance, created, **kwargs):
    """
    Log model save completion.
    """
    if not sender._meta.app_label == 'contenttypes':
        action = "Created" if created else "Updated"
        print(f"✅ {action} {sender.__name__}: {instance}")


# Error handling signals
@receiver(post_save)
def handle_save_errors(sender, instance, **kwargs):
    """
    Global error handling for save operations.
    """
    # This would integrate with error tracking services like Sentry
    pass
