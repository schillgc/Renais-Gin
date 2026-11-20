import os
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from .forms import (
    BottleRegistrationForm,
    CommunityCircleForm,
    PDFUploadForm,
    PledgeSubmissionForm,
)
from .models import (
    Bottle,
    CommunityCircle,
    GeneratedReport,
    KarmaPledge,
    MovementMetrics,
    PledgeVote,
    UserPDFDocument,
)
from .services import KarmaValidationService, MovementMetricsService, PersonalizationService


@login_required
def dashboard(request):
    """User dashboard view"""
    user_bottles = Bottle.objects.filter(registered_to=request.user).select_related('registered_to')
    user_pledges = KarmaPledge.objects.filter(user=request.user).select_related('bottle')

    # Find bottles without pledges
    bottles_without_pledges = user_bottles.exclude(
        id__in=user_pledges.values_list('bottle_id', flat=True)
    )

    # Get personalized recommendations
    recommendations = PersonalizationService.generate_recommendations(request.user)

    # Get movement metrics
    metrics = MovementMetrics.objects.filter(pk=1).first()

    context = {
        'user_bottles': user_bottles,
        'user_pledges': user_pledges,
        'bottles_without_pledges': bottles_without_pledges,
        'recommendations': recommendations,
        'metrics': metrics,
    }

    return render(request, 'core/dashboard.html', context)


@login_required
def register_bottle(request):
    """Register a new bottle and redirect to pledge page"""
    form = BottleRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        bottle_id = form.cleaned_data['bottle_id']
        with transaction.atomic():
            bottle = Bottle.objects.select_for_update().filter(bottle_id=bottle_id).first()
            if bottle is None:
                form.add_error('bottle_id', 'Invalid bottle ID.')
            elif bottle.registered:
                form.add_error('bottle_id', 'This bottle has already been registered.')
            else:
                bottle.registered = True
                bottle.registered_to = request.user
                bottle.registration_date = timezone.now()
                bottle.save(update_fields=['registered', 'registered_to', 'registration_date'])
                messages.success(request, 'Bottle registered successfully! Now make your pledge.')
                return redirect('core:submit_pledge', bottle_id=bottle.bottle_id)

    return render(request, 'core/register_bottle.html', {'form': form})


@login_required
def submit_pledge(request, bottle_id):
    """Submit a karma pledge for a bottle"""
    bottle = get_object_or_404(Bottle, bottle_id=bottle_id, registered_to=request.user)

    if KarmaPledge.objects.filter(user=request.user, bottle=bottle).exists():
        if request.method == 'POST':
            messages.error(request, 'You have already submitted a pledge for this bottle.')
        return redirect('core:dashboard')

    form = PledgeSubmissionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        validation_result = KarmaValidationService.validate_submission(
            form.cleaned_data['pledge_text'],
            form.cleaned_data['impact_plan'],
        )
        if validation_result['status'] == 'rejected':
            messages.error(request, f"Pledge pre-screened: {validation_result['reason']}")
            return redirect('core:dashboard')

        pledge = form.save(commit=False)
        pledge.user = request.user
        pledge.bottle = bottle
        pledge.impact_type = KarmaValidationService.classify_impact_type(pledge.impact_plan)
        pledge.status = 'needs_review'
        try:
            with transaction.atomic():
                pledge.save()
        except IntegrityError:
            messages.error(request, 'You have already submitted a pledge for this bottle.')
            return redirect('core:dashboard')

        messages.success(request, 'Pledge submitted successfully! It will now be reviewed by the community.')
        return redirect('core:dashboard')

    return render(request, 'core/submit_pledge.html', {'bottle': bottle, 'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def validate_pledge(request, pledge_id):
    """Record one independent community review per account."""
    pledge = get_object_or_404(KarmaPledge, id=pledge_id)

    if request.method == 'POST':
        # Lock the pledge while checking and recording a vote so concurrent
        # requests from the same account cannot count twice on databases that
        # support SELECT ... FOR UPDATE.
        with transaction.atomic():
            pledge = get_object_or_404(
                KarmaPledge.objects.select_for_update(),
                id=pledge_id
            )

            if request.user == pledge.user:
                messages.error(request, 'You cannot validate your own pledge.')
                return redirect('core:dashboard')

            if pledge.status in ('approved', 'rejected'):
                messages.error(request, 'This pledge is already closed for review.')
                return redirect('core:dashboard')

            if PledgeVote.objects.filter(pledge=pledge, voter=request.user).exists():
                messages.error(request, 'You have already validated this pledge.')
                return redirect('core:dashboard')

            approval = request.POST.get('approval') == 'true'
            comments = request.POST.get('comments', '')
            PledgeVote.objects.create(
                pledge=pledge,
                voter=request.user,
                approval=approval,
                comments=comments[:2000],
            )
            validations = list(pledge.validations or [])
            validations.append({
                'validator_id': request.user.id,
                'validator_username': request.user.username,
                'approval': approval,
                'comments': comments[:2000],
                'timestamp': timezone.now().isoformat(),
            })
            pledge.validations = validations
            approval_count = PledgeVote.objects.filter(pledge=pledge, approval=True).count()
            pledge.approvals = approval_count

            if approval_count >= 3:
                pledge.status = 'approved'
                messages.success(
                    request,
                    'Pledge approved by the community. No rebate has been processed; '
                    'this prototype has no payment integration.'
                )
            else:
                messages.success(request, 'Validation recorded successfully.')
            rejection_count = PledgeVote.objects.filter(pledge=pledge, approval=False).count()
            if rejection_count >= 3:
                pledge.status = 'rejected'

            pledge.save(update_fields=['validations', 'approvals', 'status'])

        return redirect('core:dashboard')

    if request.user == pledge.user:
        messages.error(request, 'You cannot validate your own pledge.')
        return redirect('core:dashboard')

    context = {
        'pledge': pledge,
    }

    return render(request, 'core/validate_pledge.html', context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created. Sign in to continue.')
        return redirect('login')
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def circle_list(request):
    circles = CommunityCircle.objects.prefetch_related('members').select_related('leader').order_by('name')
    return render(request, 'core/circle_list.html', {'circles': circles})


@login_required
def circle_detail(request, circle_id):
    circle = get_object_or_404(
        CommunityCircle.objects.prefetch_related('members').select_related('leader'),
        id=circle_id,
    )
    is_member = circle.members.filter(id=request.user.id).exists()
    return render(request, 'core/circle_detail.html', {
        'circle': circle,
        'is_member': is_member,
    })


@login_required
def circle_create(request):
    form = CommunityCircleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        circle = form.save(commit=False)
        circle.leader = request.user
        circle.save()
        circle.members.add(request.user)
        messages.success(request, 'Community circle created.')
        return redirect('core:circle_detail', circle_id=circle.id)
    return render(request, 'core/circle_form.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def circle_join(request, circle_id):
    circle = get_object_or_404(CommunityCircle, id=circle_id)
    circle.members.add(request.user)
    messages.success(request, f'Joined {circle.name}.')
    return redirect('core:circle_detail', circle_id=circle.id)


@login_required
@require_http_methods(["POST"])
def circle_leave(request, circle_id):
    circle = get_object_or_404(CommunityCircle, id=circle_id)
    if circle.leader_id == request.user.id:
        messages.error(request, 'The circle leader cannot leave while leading the circle.')
    else:
        circle.members.remove(request.user)
        messages.success(request, f'Left {circle.name}.')
    return redirect('core:circle_detail', circle_id=circle.id)


@require_GET
def api_movement_metrics(request):
    """Return the last stored aggregate without mutating metrics on a public request."""
    metrics = MovementMetrics.objects.filter(pk=1).first()

    data = {
        'total_pledges': metrics.total_pledges if metrics else 0,
        'total_rebates': metrics.total_rebates if metrics else 0,
        'community_size': metrics.community_size if metrics else 0,
        'impact_stories': metrics.impact_stories if metrics else 0,
        'global_reach': metrics.global_reach if metrics else {},
        'last_updated': metrics.last_updated.isoformat() if metrics else None,
    }

    return JsonResponse(data)


@login_required
def upload_pdf(request):
    """Handle PDF uploads from users"""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_doc = form.save(commit=False)
            pdf_doc.user = request.user
            pdf_doc.save()
            messages.success(request, 'PDF uploaded successfully! It will be verified by our team.')
            return redirect('core:dashboard')
    else:
        form = PDFUploadForm()

    context = {'form': form}
    return render(request, 'core/upload_pdf.html', context)


@login_required
def download_pdf(request, pdf_id):
    """Download a PDF file"""
    pdf_doc = get_object_or_404(UserPDFDocument, id=pdf_id, user=request.user)

    if os.path.exists(pdf_doc.pdf_file.path):
        response = FileResponse(pdf_doc.pdf_file.open(), content_type='application/pdf')
        safe_title = "".join(
            character for character in pdf_doc.title
            if character.isalnum() or character in (" ", "-", "_")
        ).strip() or "document"
        response['Content-Disposition'] = f'attachment; filename="{safe_title}.pdf"'
        return response
    else:
        messages.error(request, 'The requested file does not exist.')
        return redirect('core:dashboard')


@login_required
def download_report(request, report_id):
    report = get_object_or_404(
        GeneratedReport,
        id=report_id,
        related_pledge__user=request.user,
    )
    if not report.pdf_file or not os.path.exists(report.pdf_file.path):
        messages.error(request, 'The requested report does not exist.')
        return redirect('core:dashboard')
    response = FileResponse(report.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.title[:80]}.pdf"'
    return response


def view_static_pdf(request, pdf_name):
    """Serve static PDF files (terms, guides, etc.)"""
    pdf_dir = (Path(settings.STATIC_ROOT) / 'pdfs').resolve()
    pdf_path = (pdf_dir / pdf_name).resolve()

    if pdf_path.is_relative_to(pdf_dir) and pdf_path.is_file():
        response = FileResponse(pdf_path.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{pdf_path.name}"'
        return response
    return HttpResponse('PDF not found', status=404)


@login_required
def generate_impact_report(request, pledge_id=None):
    """Generate a PDF impact report"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    # Get pledge data if provided
    pledge = None
    if pledge_id:
        pledge = get_object_or_404(KarmaPledge, id=pledge_id, user=request.user)

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Container for the 'Flowable' objects
    story = []

    # Add content to the PDF
    styles = getSampleStyleSheet()
    story.append(Paragraph("Renais Gin Impact Report", styles['Title']))
    story.append(Spacer(1, 12))

    if pledge:
        story.append(Paragraph(f"Pledge: {pledge.pledge_text}", styles['BodyText']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Impact Plan: {pledge.impact_plan}", styles['BodyText']))
    else:
        # Generate a general user report
        user_pledges = KarmaPledge.objects.filter(user=request.user)
        profile = getattr(request.user, 'userprofile', None)
        story.append(Paragraph(f"User: {request.user.username}", styles['BodyText']))
        story.append(Paragraph(f"Total Pledges: {user_pledges.count()}", styles['BodyText']))
        karma_score = profile.karma_score if profile else 0.0
        story.append(Paragraph(f"Karma Score: {karma_score}", styles['BodyText']))

    # Build PDF
    doc.build(story)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file
    buffer.seek(0)

    # Create a GeneratedReport record
    if pledge:
        title = f"Impact Report for Pledge {pledge.submission_id}"
    else:
        title = f"Impact Report for {request.user.username}"

    report = GeneratedReport.objects.create(
        report_type='impact',
        title=title,
        related_pledge=pledge
    )

    # Save the PDF to the report
    report.pdf_file.save(f'report_{report.id}.pdf', ContentFile(buffer.getvalue()))

    # Return the PDF as a response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="renais_impact_report.pdf"'
    response.write(buffer.getvalue())
    return response

def custom_404_view(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500_view(request):
    return render(request, 'core/500.html', status=500)
