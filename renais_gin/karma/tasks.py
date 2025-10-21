# karma/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import KarmaPledge, KarmaRebate


@shared_task
def process_ai_validation(pledge_id):
    """Async task to process AI validation of a pledge"""
    from ..ai_agents.services import AIService
    from .models import KarmaPledge

    try:
        pledge = KarmaPledge.objects.get(id=pledge_id)
        ai_service = AIService()

        result = ai_service.validate_pledge(pledge.pledge_text, pledge.impact_plan)

        # Update pledge with AI results
        pledge.ai_confidence_score = result.get('score')
        if result.get('status') != 'approved':
            pledge.status = KarmaPledge.STATUS_NEEDS_REVIEW

        pledge.save()

        # Send notification if needed
        if result.get('status') == 'rejected':
            send_pledge_notification.delay(
                pledge.user.email,
                'Pledge Requires Review',
                f'Your pledge {pledge.submission_id} requires additional review.'
            )

        return f"AI validation completed for pledge {pledge_id}"

    except KarmaPledge.DoesNotExist:
        return f"Pledge {pledge_id} not found"


@shared_task
def send_pledge_notification(email, subject, message):
    """Send email notification about pledge status"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )


@shared_task
def process_rebate_payments():
    """Process pending rebate payments (run periodically)"""
    from .models import KarmaRebate
    from django.utils import timezone

    pending_rebates = KarmaRebate.objects.filter(status=KarmaRebate.STATUS_PENDING)

    for rebate in pending_rebates:
        try:
            # Simulate payment processing
            # In production, integrate with payment processor like Stripe
            rebate.status = KarmaRebate.STATUS_PROCESSED
            rebate.processed_date = timezone.now()
            rebate.transaction_id = f"tx_{rebate.id}_{int(timezone.now().timestamp())}"
            rebate.save()

            # Send confirmation
            send_pledge_notification.delay(
                rebate.user.email,
                'Rebate Processed',
                f'Your ${rebate.amount} rebate for pledge {rebate.pledge.submission_id} has been processed.'
            )

        except Exception as e:
            print(f"Failed to process rebate {rebate.id}: {str(e)}")
            rebate.status = KarmaRebate.STATUS_FAILED
            rebate.save()
