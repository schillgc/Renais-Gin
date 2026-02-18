"""
Celery tasks for Renais Gin core application.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import logging

from django.contrib.auth import get_user_model
User = get_user_model()

from .services import RenaisGinService
from .models import KarmaPledge, Rebate, User, PledgeValidation, MovementMetrics

logger = logging.getLogger(__name__)


@shared_task
def update_movement_metrics():
    """
    Periodic task to update and cache movement metrics.
    Runs every hour.
    """
    try:
        service = RenaisGinService()
        metrics = service.get_movement_metrics()

        # Update or create MovementMetrics record
        movement_metrics, created = MovementMetrics.objects.get_or_create(
            id=1,  # Single record for global metrics
            defaults=metrics
        )

        if not created:
            # Update existing record
            for key, value in metrics.items():
                setattr(movement_metrics, key, value)
            movement_metrics.save()

        logger.info(f"Movement metrics updated: {metrics}")
        return metrics

    except Exception as e:
        logger.error(f"Error updating movement metrics: {e}")
        return {'error': str(e)}


@shared_task
def process_pending_validations():
    """
    Process pending validations and update pledge statuses.
    Runs every 30 minutes.
    """
    try:
        from .models import KarmaPledge

        pending_pledges = KarmaPledge.objects.filter(status='pending')
        processed_count = 0

        for pledge in pending_pledges:
            service = RenaisGinService()
            service._update_pledge_status(pledge)
            processed_count += 1

        logger.info(f"Processed {processed_count} pending validations")
        return {'processed_count': processed_count}

    except Exception as e:
        logger.error(f"Error processing pending validations: {e}")
        return {'error': str(e)}


@shared_task
def send_pledge_status_notification(pledge_id):
    """
    Send email notification when pledge status changes.
    """
    try:
        pledge = KarmaPledge.objects.get(id=pledge_id)
        user = pledge.user

        if pledge.status == 'approved':
            subject = "🎉 Your Renais Gin Pledge Has Been Approved!"
            message = f"""
Hello {user.username},

Great news! Your pledge has been approved by the Renais Gin community.

Pledge: "{pledge.pledge_text[:100]}..."

Your ${pledge.rebate.amount if hasattr(pledge, 'rebate') else 5.00} rebate is now being processed and should be completed within 3-5 business days.

Thank you for being part of the Renais Gin movement and for your commitment to creating positive impact in the world.

Craft Your Perfect World,
The Renais Gin Team
            """

        elif pledge.status == 'rejected':
            subject = "Update on Your Renais Gin Pledge"
            message = f"""
Hello {user.username},

After community review, your pledge "{pledge.pledge_text[:100]}..." did not receive enough approvals to move forward.

We encourage you to:
1. Review the community feedback
2. Add more specific details to your impact plan
3. Resubmit your pledge with clearer implementation steps

You can view feedback and resubmit at: [Your Dashboard Link]

Thank you for your understanding and continued participation.

Craft Your Perfect World,
The Renais Gin Team
            """
        else:
            return  # No notification for other statuses

        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Sent status notification for pledge {pledge_id} to {user.email}")
        return {'sent': True, 'pledge_id': pledge_id, 'user_id': user.id}

    except KarmaPledge.DoesNotExist:
        logger.error(f"Pledge {pledge_id} not found for notification")
        return {'error': 'Pledge not found'}
    except Exception as e:
        logger.error(f"Error sending notification for pledge {pledge_id}: {e}")
        return {'error': str(e)}


@shared_task
def process_rebate_payments():
    """
    Process pending rebate payments.
    Runs daily at 2 AM.
    """
    try:
        pending_rebates = Rebate.objects.filter(status='pending')[:20]  # Process 20 at a time
        processed_count = 0
        failed_count = 0

        for rebate in pending_rebates:
            try:
                # Mark as processing
                rebate.mark_processing()

                # Simulate payment processing
                # In production, integrate with actual payment processor like Stripe, PayPal, etc.
                service = RenaisGinService()
                result = service.process_rebate_payment(rebate.id)

                if result['success']:
                    processed_count += 1
                    # Send notification
                    send_rebate_processed_notification.delay(rebate.id)
                    logger.info(f"Processed rebate {rebate.id}")
                else:
                    rebate.mark_failed()
                    failed_count += 1
                    logger.error(f"Failed to process rebate {rebate.id}: {result['error']}")

            except Exception as e:
                rebate.mark_failed()
                failed_count += 1
                logger.error(f"Error processing rebate {rebate.id}: {e}")

        logger.info(f"Rebate processing completed: {processed_count} processed, {failed_count} failed")
        return {
            'processed_count': processed_count,
            'failed_count': failed_count,
            'total_processed': processed_count + failed_count
        }

    except Exception as e:
        logger.error(f"Error in rebate processing task: {e}")
        return {'error': str(e)}


@shared_task
def send_rebate_processed_notification(rebate_id):
    """
    Send email notification when rebate is processed.
    """
    try:
        rebate = Rebate.objects.get(id=rebate_id)
        user = rebate.pledge.user

        subject = "💰 Your Renais Gin Rebate Has Been Processed!"

        message = f"""
Hello {user.username},

Great news! Your ${rebate.amount} rebate has been successfully processed.

Transaction Details:
- Amount: ${rebate.amount}
- Transaction ID: {rebate.transaction_id}
- Processed on: {rebate.processed_date.strftime('%B %d, %Y') if rebate.processed_date else 'N/A'}
- Pledge: "{rebate.pledge.pledge_text[:100]}..."

The funds should appear in your account within 1-3 business days, depending on your payment method.

Thank you for creating positive impact with Renais Gin! Your commitment to making a difference is what drives our community forward.

Craft Your Perfect World,
The Renais Gin Team
        """

        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Sent rebate notification for {rebate_id} to {user.email}")
        return {'sent': True, 'rebate_id': rebate_id}

    except Rebate.DoesNotExist:
        logger.error(f"Rebate {rebate_id} not found for notification")
        return {'error': 'Rebate not found'}
    except Exception as e:
        logger.error(f"Error sending rebate notification for {rebate_id}: {e}")
        return {'error': str(e)}


@shared_task
def update_user_engagement_scores():
    """
    Periodic task to update all user engagement scores.
    Runs daily at 3 AM.
    """
    try:
        users = User.objects.filter(is_active=True)
        updated_count = 0

        for user in users:
            try:
                service = RenaisGinService()
                service._update_user_engagement(user)
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating engagement score for user {user.id}: {e}")

        logger.info(f"Updated engagement scores for {updated_count} users")
        return {'updated_count': updated_count}

    except Exception as e:
        logger.error(f"Error in engagement score update task: {e}")
        return {'error': str(e)}


@shared_task
def cleanup_old_data():
    """
    Clean up old data and maintain database performance.
    Runs weekly on Sunday at 4 AM.
    """
    try:
        from django.utils import timezone
        from datetime import timedelta

        # Delete very old validation records (keep 6 months)
        cutoff_date = timezone.now() - timedelta(days=180)
        old_validations = PledgeValidation.objects.filter(created_at__lt=cutoff_date)
        deleted_validations_count = old_validations.count()
        old_validations.delete()

        # Archive old PDF documents (keep 1 year)
        pdf_cutoff = timezone.now() - timedelta(days=365)
        old_pdfs = UserPDFDocument.objects.filter(uploaded_at__lt=pdf_cutoff, is_verified=False)
        deleted_pdfs_count = old_pdfs.count()
        old_pdfs.delete()

        # Clean up old session data
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        session_cutoff = timezone.now() - timedelta(days=30)
        old_sessions = Session.objects.filter(expire_date__lt=session_cutoff)
        deleted_sessions_count = old_sessions.count()
        old_sessions.delete()

        logger.info(
            f"Data cleanup completed: {deleted_validations_count} validations, {deleted_pdfs_count} PDFs, {deleted_sessions_count} sessions removed")
        return {
            'deleted_validations': deleted_validations_count,
            'deleted_pdfs': deleted_pdfs_count,
            'deleted_sessions': deleted_sessions_count
        }

    except Exception as e:
        logger.error(f"Error in data cleanup task: {e}")
        return {'error': str(e)}


@shared_task
def send_weekly_newsletter():
    """
    Send weekly newsletter to active users.
    Runs every Monday at 9 AM.
    """
    try:
        # Get active users who haven't opted out of newsletters
        active_users = User.objects.filter(
            is_active=True,
            profile__preferences__newsletter=True  # Assuming preference field
        )

        sent_count = 0
        service = RenaisGinService()
        movement_metrics = service.get_movement_metrics()

        for user in active_users:
            try:
                user_metrics = service.get_user_metrics(user)

                subject = "📊 Your Renais Gin Weekly Impact Report"

                message = f"""
Hello {user.username},

Here's your weekly update from the Renais Gin community:

Your Impact This Week:
- Total Pledges: {user_metrics.get('total_pledges', 0)}
- Approved Pledges: {user_metrics.get('approved_pledges', 0)}
- Total Impact: ${user_metrics.get('total_impact', 0)}
- Engagement Score: {user_metrics.get('engagement_score', 0)}

Global Movement Update:
- Community Size: {movement_metrics.get('total_community', 0)}
- Total Pledges: {movement_metrics.get('total_pledges', 0)}
- Total Impact: ${movement_metrics.get('total_impact', 0)}
- Active Circles: {movement_metrics.get('active_circles', 0)}

Keep making a difference!
The Renais Gin Team
                """

                send_mail(
                    subject,
                    message.strip(),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                sent_count += 1

            except Exception as e:
                logger.error(f"Error sending newsletter to user {user.id}: {e}")

        logger.info(f"Weekly newsletter sent to {sent_count} users")
        return {'sent_count': sent_count}

    except Exception as e:
        logger.error(f"Error in weekly newsletter task: {e}")
        return {'error': str(e)}


@shared_task
def generate_daily_reports():
    """
    Generate daily activity reports for admin review.
    Runs daily at 6 AM.
    """
    try:
        from datetime import datetime, timedelta
        yesterday = timezone.now() - timedelta(days=1)

        # Gather daily statistics
        new_users = User.objects.filter(date_joined__gte=yesterday).count()
        new_pledges = KarmaPledge.objects.filter(created_at__gte=yesterday).count()
        approved_pledges = KarmaPledge.objects.filter(
            status='approved',
            updated_at__gte=yesterday
        ).count()
        processed_rebates = Rebate.objects.filter(
            status='completed',
            processed_date__gte=yesterday
        ).count()

        report_data = {
            'date': yesterday.strftime('%Y-%m-%d'),
            'new_users': new_users,
            'new_pledges': new_pledges,
            'approved_pledges': approved_pledges,
            'processed_rebates': processed_rebates,
            'total_rebate_amount': processed_rebates * settings.RENAIS_SETTINGS['REBATE_AMOUNT'],
            'generated_at': timezone.now().isoformat()
        }

        logger.info(f"Daily report generated: {report_data}")
        return report_data

    except Exception as e:
        logger.error(f"Error generating daily reports: {e}")
        return {'error': str(e)}
