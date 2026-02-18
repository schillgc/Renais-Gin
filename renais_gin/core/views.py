# core/views.py
"""
Views for Renais Gin core application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from .models import (
    User, UserProfile, Bottle, KarmaPledge, PledgeValidation,
    Rebate, CommunityCircle, UserPDFDocument, GeneratedReport
)
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    UserLoginSerializer, BottleSerializer, KarmaPledgeSerializer,
    PledgeValidationSerializer, RebateSerializer, CommunityCircleSerializer,
    UserPDFDocumentSerializer, GeneratedReportSerializer,
    UserMetricsSerializer, MovementMetricsSerializer
)
from .services import RenaisGinService, CommunityService
from .forms import (
    PDFUploadForm, PledgeForm, CommunityCircleForm,
    UserProfileForm, ValidationForm, BottleRegistrationForm
)


# Template Views
def home_view(request):
    """Home page view"""
    service = RenaisGinService()
    metrics = service.get_movement_metrics()
    return render(request, 'core/home.html', {
        'movement_metrics': metrics
    })


def about_view(request):
    """About page view"""
    return render(request, 'about.html')


@login_required
def dashboard_view(request):
    """User dashboard view"""
    service = RenaisGinService()
    user_metrics = service.get_user_metrics(request.user)
    movement_metrics = service.get_movement_metrics()

    # Get recent pledges
    recent_pledges = KarmaPledge.objects.filter(user=request.user)[:5]

    # Get bottles needing validation
    validation_pledges = KarmaPledge.objects.filter(
        status='pending'
    ).exclude(
        user=request.user
    ).exclude(
        validations__validator=request.user
    )[:5]

    return render(request, 'core/dashboard.html', {
        'user_metrics': user_metrics,
        'movement_metrics': movement_metrics,
        'recent_pledges': recent_pledges,
        'validation_pledges': validation_pledges,
    })


@login_required
def bottles_view(request):
    """User's bottles view"""
    bottles = Bottle.objects.filter(registered_to=request.user).order_by('-registration_date')

    # Pagination
    paginator = Paginator(bottles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/bottles.html', {
        'bottles': page_obj,
    })


@login_required
def bottle_detail_view(request, bottle_id):
    """Bottle detail view"""
    bottle = get_object_or_404(Bottle, bottle_id=bottle_id, registered_to=request.user)
    pledge = bottle.pledges.first() if bottle.pledges.exists() else None

    return render(request, 'core/bottle_detail.html', {
        'bottle': bottle,
        'pledge': pledge,
    })


@login_required
def register_bottle_view(request):
    """Bottle registration view"""
    if request.method == 'POST':
        form = BottleRegistrationForm(request.POST)
        if form.is_valid():
            bottle_id = form.cleaned_data['bottle_id']
            service = RenaisGinService()

            # Get bottle data (in real app, this would come from QR scan)
            bottle_data = {
                'bottle_id': bottle_id,
                'batch_id': 'BATCH_001',  # This would be from the bottle record
                'production_date': '2023-01-01',  # This would be from the bottle record
            }

            result = service.register_bottle(bottle_data, request.user)

            if result['success']:
                messages.success(request, 'Bottle registered successfully!')
                return redirect('core:bottle_detail', bottle_id=bottle_id)
            else:
                messages.error(request, result['error'])
    else:
        form = BottleRegistrationForm()

    return render(request, 'core/register_bottle.html', {'form': form})


@login_required
def karma_view(request):
    """Karma pledges overview"""
    pledges = KarmaPledge.objects.filter(user=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(pledges, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/karma.html', {
        'pledges': page_obj,
    })


@login_required
def submit_pledge_view(request, bottle_id):
    """Submit a pledge for a bottle"""
    bottle = get_object_or_404(Bottle, bottle_id=bottle_id, registered_to=request.user)

    if not bottle.can_make_pledge():
        messages.error(request, 'This bottle cannot make a pledge.')
        return redirect('core:bottle_detail', bottle_id=bottle_id)

    if request.method == 'POST':
        form = PledgeForm(request.POST)
        if form.is_valid():
            service = RenaisGinService()
            result = service.submit_pledge(
                request.user,
                bottle_id,
                form.cleaned_data['pledge_text'],
                form.cleaned_data['impact_plan']
            )

            if result['success']:
                messages.success(request, 'Pledge submitted successfully!')
                return redirect('core:pledge_detail', pledge_id=result['pledge'].id)
            else:
                messages.error(request, result['error'])
    else:
        form = PledgeForm()

    return render(request, 'core/submit_pledge.html', {
        'form': form,
        'bottle': bottle,
    })


@login_required
def pledge_detail_view(request, pledge_id):
    """Pledge detail view"""
    pledge = get_object_or_404(KarmaPledge, id=pledge_id, user=request.user)
    validations = pledge.validations.all()

    return render(request, 'core/pledge_detail.html', {
        'pledge': pledge,
        'validations': validations,
    })


@login_required
def validate_pledge_view(request, pledge_id):
    """Validate a community pledge"""
    pledge = get_object_or_404(KarmaPledge, id=pledge_id)

    # Check if user can validate this pledge
    if pledge.user == request.user:
        messages.error(request, 'You cannot validate your own pledge.')
        return redirect('core:community_pledges')

    if PledgeValidation.objects.filter(pledge=pledge, validator=request.user).exists():
        messages.error(request, 'You have already validated this pledge.')
        return redirect('core:community_pledges')

    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid():
            service = RenaisGinService()
            result = service.validate_pledge(
                request.user,
                pledge_id,
                form.cleaned_data['approval'],
                form.cleaned_data['comments'],
                get_client_ip(request),
                request.META.get('HTTP_USER_AGENT', '')
            )

            if result['success']:
                action = "approved" if form.cleaned_data['approval'] else "rejected"
                messages.success(request, f'Pledge {action} successfully!')
                return redirect('core:community_pledges')
            else:
                messages.error(request, result['error'])
    else:
        form = ValidationForm()

    return render(request, 'core/validate_pledge.html', {
        'form': form,
        'pledge': pledge,
    })


@login_required
def community_pledges_view(request):
    """Community pledges for validation"""
    pledges = KarmaPledge.objects.filter(
        status='pending'
    ).exclude(
        user=request.user
    ).exclude(
        validations__validator=request.user
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(pledges, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/community_pledges.html', {
        'pledges': page_obj,
    })


@login_required
def community_circles_view(request):
    """Community circles overview"""
    circles = CommunityCircle.objects.filter(is_active=True).order_by('-created_at')
    user_circles = request.user.community_circles.filter(is_active=True)
    led_circles = request.user.led_circles.filter(is_active=True)

    return render(request, 'core/community_circles.html', {
        'circles': circles,
        'user_circles': user_circles,
        'led_circles': led_circles,
    })


@login_required
def create_circle_view(request):
    """Create a community circle"""
    if request.method == 'POST':
        form = CommunityCircleForm(request.POST)
        if form.is_valid():
            service = CommunityService()
            result = service.create_community_circle(
                form.cleaned_data['name'],
                form.cleaned_data['location'],
                request.user,
                form.cleaned_data['description']
            )

            if result['success']:
                messages.success(request, 'Community circle created successfully!')
                return redirect('core:circle_detail', circle_id=result['circle'].id)
            else:
                messages.error(request, result['error'])
    else:
        form = CommunityCircleForm()

    return render(request, 'core/create_circle.html', {'form': form})


@login_required
def circle_detail_view(request, circle_id):
    """Community circle detail"""
    circle = get_object_or_404(CommunityCircle, id=circle_id, is_active=True)
    is_member = circle.members.filter(id=request.user.id).exists()
    is_leader = circle.leader == request.user

    return render(request, 'core/circle_detail.html', {
        'circle': circle,
        'is_member': is_member,
        'is_leader': is_leader,
    })


@login_required
def join_circle_view(request, circle_id):
    """Join a community circle"""
    service = CommunityService()
    result = service.join_community_circle(request.user, circle_id)

    if result['success']:
        messages.success(request, 'Successfully joined the community circle!')
    else:
        messages.error(request, result['error'])

    return redirect('core:circle_detail', circle_id=circle_id)


@login_required
def leave_circle_view(request, circle_id):
    """Leave a community circle"""
    service = CommunityService()
    result = service.leave_community_circle(request.user, circle_id)

    if result['success']:
        messages.success(request, 'Successfully left the community circle!')
    else:
        messages.error(request, result['error'])

    return redirect('core:community_circles')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user.profile, user=request.user)

    service = RenaisGinService()
    user_metrics = service.get_user_metrics(request.user)

    return render(request, 'core/profile.html', {
        'form': form,
        'user_metrics': user_metrics,
    })


@login_required
def upload_pdf_view(request):
    """Upload PDF document"""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_doc = form.save(commit=False)
            pdf_doc.user = request.user
            pdf_doc.save()
            messages.success(request, 'PDF uploaded successfully!')
            return redirect('core:my_documents')
    else:
        form = PDFUploadForm()

    return render(request, 'core/upload_pdf.html', {'form': form})


@login_required
def my_documents_view(request):
    """User's documents view"""
    documents = UserPDFDocument.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'core/my_documents.html', {'documents': documents})


@login_required
def leaderboard_view(request):
    """Community leaderboard"""
    # Top users by karma score
    top_users = UserProfile.objects.select_related('user').order_by('-karma_score')[:20]

    # Top circles by member count
    top_circles = CommunityCircle.objects.filter(is_active=True).annotate(
        member_count=Count('members')
    ).order_by('-member_count')[:10]

    return render(request, 'core/leaderboard.html', {
        'top_users': top_users,
        'top_circles': top_circles,
    })


@login_required
def impact_stories_view(request):
    """Impact stories from the community"""
    approved_pledges = KarmaPledge.objects.filter(
        status='approved'
    ).select_related('user').order_by('-created_at')

    # Group by impact type
    impact_stories = {}
    for pledge in approved_pledges:
        if pledge.impact_type not in impact_stories:
            impact_stories[pledge.impact_type] = []
        impact_stories[pledge.impact_type].append(pledge)

    return render(request, 'core/impact_stories.html', {
        'impact_stories': impact_stories,
    })


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('core:dashboard')
        else:
            # Pass form errors to template
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        serializer = UserRegistrationSerializer()

    return render(request, 'core/register.html', {
        'form': serializer
    })


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        serializer = UserLoginSerializer()

    return render(request, 'core/login.html', {
        'form': serializer
    })


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('core:home')


# API Views
class UserProfileViewSet(viewsets.ModelViewSet):
    """API viewset for user profiles"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get user metrics"""
        service = RenaisGinService()
        metrics = service.get_user_metrics(request.user)
        serializer = UserMetricsSerializer(metrics)
        return Response(serializer.data)


class BottleViewSet(viewsets.ModelViewSet):
    """API viewset for bottles"""
    serializer_class = BottleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bottle.objects.filter(registered_to=self.request.user)

    def perform_create(self, serializer):
        # Bottle registration handled by service
        pass


class KarmaPledgeViewSet(viewsets.ModelViewSet):
    """API viewset for karma pledges"""
    serializer_class = KarmaPledgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KarmaPledge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Pledge submission handled by service
        pass


class CommunityCircleViewSet(viewsets.ModelViewSet):
    """API viewset for community circles"""
    serializer_class = CommunityCircleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommunityCircle.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(leader=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movement_metrics_api(request):
    """API endpoint for movement metrics"""
    service = RenaisGinService()
    metrics = service.get_movement_metrics()
    serializer = MovementMetricsSerializer(metrics)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user_api(request):
    """API endpoint for user registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user_api(request):
    """API endpoint for user login"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user_api(request):
    """API endpoint for user logout"""
    logout(request)
    return Response({'message': 'Logout successful'})


# Utility functions
def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Error handlers
def custom_404_view(request, exception):
    return render(request, 'core/404.html', status=404)


def custom_500_view(request):
    return render(request, 'core/500.html', status=500)
