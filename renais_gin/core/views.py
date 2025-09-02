from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Bottle, KarmaPledge, UserProfile, MovementMetrics
from .services import KarmaValidationService, PersonalizationService, MovementMetricsService
import json
from django.http import FileResponse, HttpResponse
from django.conf import settings
import os
from .models import UserPDFDocument, GeneratedReport


@login_required
def dashboard(request):
    """User dashboard view"""
    user_bottles = Bottle.objects.filter(registered_to=request.user)
    user_pledges = KarmaPledge.objects.filter(user=request.user)

    # Find bottles without pledges
    bottles_without_pledges = user_bottles.exclude(
        id__in=user_pledges.values_list('bottle_id', flat=True)
    )

    # Get personalized recommendations
    recommendations = PersonalizationService.generate_recommendations(request.user)

    # Get movement metrics
    metrics = MovementMetricsService.update_metrics()

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
    if request.method == 'POST':
        bottle_id = request.POST.get('bottle_id')

        try:
            bottle = Bottle.objects.get(bottle_id=bottle_id)

            if bottle.registered:
                messages.error(request, 'This bottle has already been registered.')
                return redirect('register_bottle')
            else:
                bottle.registered = True
                bottle.registered_to = request.user
                bottle.registration_date = timezone.now()
                bottle.save()

                messages.success(request, 'Bottle registered successfully! Now make your pledge.')
                # Redirect to the pledge page for this bottle
                return redirect('submit_pledge', bottle_id=bottle.bottle_id)

        except Bottle.DoesNotExist:
            messages.error(request, 'Invalid bottle ID.')

    return render(request, 'core/register_bottle.html')


@login_required
def submit_pledge(request, bottle_id):
    """Submit a karma pledge for a bottle"""
    bottle = get_object_or_404(Bottle, bottle_id=bottle_id, registered_to=request.user)

    if request.method == 'POST':
        pledge_text = request.POST.get('pledge_text')
        impact_plan = request.POST.get('impact_plan')

        # Validate the pledge
        validation_result = KarmaValidationService.validate_submission(pledge_text, impact_plan)

        if validation_result['status'] == 'rejected':
            messages.error(request, f"Pledge rejected: {validation_result['reason']}")
            return redirect('core:dashboard')

        # Create the pledge
        impact_type = KarmaValidationService.classify_impact_type(impact_plan)

        pledge = KarmaPledge(
            user=request.user,
            bottle=bottle,
            pledge_text=pledge_text,
            impact_plan=impact_plan,
            impact_type=impact_type,
            status=validation_result['status']
        )

        if 'score' in validation_result:
            pledge.approvals = int(validation_result['score'] * 3)  # Simulate initial approvals based on score

        pledge.save()

        messages.success(request, 'Pledge submitted successfully! It will now be reviewed by the community.')
        return redirect('core:dashboard')

    context = {
        'bottle': bottle,
    }

    return render(request, 'core/submit_pledge.html', context)


@login_required
def validate_pledge(request, pledge_id):
    """Validate another user's pledge"""
    pledge = get_object_or_404(KarmaPledge, id=pledge_id)

    if request.user == pledge.user:
        messages.error(request, 'You cannot validate your own pledge.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        approval = request.POST.get('approval') == 'true'
        comments = request.POST.get('comments', '')

        # Record validation
        validation_data = {
            'validator_id': request.user.id,
            'validator_username': request.user.username,
            'approval': approval,
            'comments': comments,
            'timestamp': timezone.now().isoformat()
        }

        pledge.validations.append(validation_data)

        if approval:
            pledge.approvals += 1

        # Check if pledge has enough approvals
        if pledge.approvals >= 3:
            pledge.status = 'approved'

            # Process rebate (in a real implementation, this would call a payment API)
            pledge.rebate_processed = True

            messages.success(request, 'Pledge approved and rebate processed!')
        else:
            messages.success(request, 'Validation recorded successfully!')

        pledge.save()
        return redirect('core:dashboard')

    context = {
        'pledge': pledge,
    }

    return render(request, 'core/validate_pledge.html', context)


@csrf_exempt
def api_movement_metrics(request):
    """API endpoint for movement metrics"""
    metrics = MovementMetricsService.update_metrics()

    data = {
        'total_pledges': metrics.total_pledges,
        'total_rebates': metrics.total_rebates,
        'community_size': metrics.community_size,
        'impact_stories': metrics.impact_stories,
        'global_reach': metrics.global_reach,
        'last_updated': metrics.last_updated.isoformat(),
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

    # Check if the file exists
    if os.path.exists(pdf_doc.pdf_file.path):
        response = FileResponse(pdf_doc.pdf_file.open(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_doc.title}.pdf"'
        return response
    else:
        messages.error(request, 'The requested file does not exist.')
        return redirect('core:dashboard')


def view_static_pdf(request, pdf_name):
    """Serve static PDF files (terms, guides, etc.)"""
    pdf_path = os.path.join(settings.STATIC_ROOT, 'pdfs', pdf_name)

    if os.path.exists(pdf_path):
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{pdf_name}"'
        return response
    else:
        return HttpResponse('PDF not found', status=404)


@login_required
def generate_impact_report(request, pledge_id=None):
    """Generate a PDF impact report"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from io import BytesIO

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
        story.append(Paragraph(f"User: {request.user.username}", styles['BodyText']))
        story.append(Paragraph(f"Total Pledges: {user_pledges.count()}", styles['BodyText']))
        story.append(Paragraph(f"Karma Score: {request.user.userprofile.karma_score}", styles['BodyText']))

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
    from django.core.files.base import ContentFile
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
