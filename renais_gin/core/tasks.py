"""
Celery tasks for Renais Gin core application.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from .services import RenaisGinService
from .models import KarmaPledge, Rebate, User


@shared_task
def update_movement_metrics():
    """
    Periodic task to update and cache movement metrics.
    """
    service = RenaisGinService()
    metrics = service.get_movement_metrics()

    # Here you could cache the metrics or update a cache table
    print(f"Movement metrics updated: {metrics}")

    return metrics


@shared_task
def process_pending_validations():
    """
    Process pending validations and update pledge statuses.
    """
    from .models import KarmaPledge

    pending_pledges = KarmaPledge.objects.filter(status='pending')

    for pledge in pending_pledges:
        service = RenaisGinService()
        service._update_pledge_status(pledge)

    print(f"Processed {pending_pledges.count()} pending validations")
    return pending_pledges.count()


@shared_task
def send_pledge_status_notification(pledge_id):
    """
    Send email notification when pledge status changes.
    """
    try:
        pledge = KarmaPledge.objects.get(id=pledge_id)
        user = pledge.user

        subject = f"Your Renais Gin Pledge Status Update"

        if pledge.status == 'approved':
            message = f"""
            Hello {user.username},

            Great news! Your pledge "{pledge.pledge_text[:50]}..." has been approved by the community.

            Your ${pledge.rebate.amount} rebate is now being processed.

            Thank you for being part of the Renais Gin movement!

            Craft Your Perfect World,
            The Renais Gin Team
            """
        elif pledge.status == 'rejected':
            message = f"""
            Hello {user.username},

            Unfortunately, your pledge "{pledge.pledge_text[:50]}..." did not receive enough community approvals.

            You can review the feedback and submit a new pledge with more specific details.

            Thank you for your understanding.

            Craft Your Perfect World,
            The Renais Gin Team
            """
        else:
            return  # No notification for other statuses

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        print(f"Sent status notification for pledge {pledge_id} to {user.email}")

    except KarmaPledge.DoesNotExist:
        print(f"Pledge {pledge_id} not found for notification")
    except Exception as e:
        print(f"Error sending notification for pledge {pledge_id}: {e}")


@shared_task
def process_rebate_payments():
    """
    Process pending rebate payments.
    """
    pending_rebates = Rebate.objects.filter(status='pending')[:10]  # Process 10 at a time

    for rebate in pending_rebates:
        try:
            # Mark as processing
            rebate.mark_processing()

            # Here you would integrate with actual payment processor
            # For now, we'll simulate successful payment
            rebate.mark_completed(transaction_id=f"TXN_{rebate.id.hex[:8]}")

            # Send notification
            send_rebate_processed_notification.delay(rebate.id)

            print(f"Processed rebate {rebate.id}")

        except Exception as e:
            print(f"Error processing rebate {rebate.id}: {e}")
            rebate.status = 'failed'
            rebate.save()

    return pending_rebates.count()


@shared_task
def send_rebate_processed_notification(rebate_id):
    """
    Send email notification when rebate is processed.
    """
    try:
        rebate = Rebate.objects.get(id=rebate_id)
        user = rebate.pledge.user

        subject = "Your Renais Gin Rebate Has Been Processed!"

        message = f"""
        Hello {user.username},

        Great news! Your ${rebate.amount} rebate for your pledge has been processed.

        Transaction ID: {rebate.transaction_id}
        Processed on: {rebate.processed_date.strftime('%B %d, %Y')}

        Thank you for creating positive impact with Renais Gin!

        Craft Your Perfect World,
        The Renais Gin Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        print(f"Sent rebate notification for {rebate_id} to {user.email}")

    except Rebate.DoesNotExist:
        print(f"Rebate {rebate_id} not found for notification")


@shared_task
def update_user_engagement_scores():
    """
    Periodic task to update all user engagement scores.
    """
    users = User.objects.filter(is_active=True)

    for user in users:
        try:
            service = RenaisGinService()
            service._update_user_engagement(user)
        except Exception as e:
            print(f"Error updating engagement score for user {user.id}: {e}")

    print(f"Updated engagement scores for {users.count()} users")
    return users.count()


@shared_task
def cleanup_old_data():
    """
    Clean up old data and maintain database performance.
    """
    from django.utils import timezone
    from datetime import timedelta

    # Delete very old validation records (keep 6 months)
    cutoff_date = timezone.now() - timedelta(days=180)
    old_validations = PledgeValidation.objects.filter(created_at__lt=cutoff_date)
    deleted_count = old_validations.count()
    old_validations.delete()

    print(f"Cleaned up {deleted_count} old validation records")
    return deleted_count
