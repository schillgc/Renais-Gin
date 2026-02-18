"""
API views for Renais Gin core application.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from django.db.models import Count, Q

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


class PledgeValidationViewSet(viewsets.ModelViewSet):
    """API viewset for pledge validations"""
    serializer_class = PledgeValidationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PledgeValidation.objects.filter(validator=self.request.user)


class RebateViewSet(viewsets.ModelViewSet):
    """API viewset for rebates"""
    serializer_class = RebateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rebate.objects.filter(pledge__user=self.request.user)


class CommunityCircleViewSet(viewsets.ModelViewSet):
    """API viewset for community circles"""
    serializer_class = CommunityCircleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommunityCircle.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(leader=self.request.user)


class UserPDFDocumentViewSet(viewsets.ModelViewSet):
    """API viewset for user PDF documents"""
    serializer_class = UserPDFDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPDFDocument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GeneratedReportViewSet(viewsets.ModelViewSet):
    """API viewset for generated reports"""
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GeneratedReport.objects.all()


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


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def leaderboard_api(request):
    """API endpoint for leaderboard"""
    # Top users by karma score
    top_users = UserProfile.objects.select_related('user').order_by('-engagement_score')[:20]

    # Top circles by member count
    top_circles = CommunityCircle.objects.filter(is_active=True).annotate(
        member_count=Count('members')
    ).order_by('-member_count')[:10]

    user_data = []
    for profile in top_users:
        user_data.append({
            'username': profile.user.username,
            'karma_score': profile.user.karma_score,
            'engagement_score': profile.engagement_score,
            'total_pledges': profile.user.pledges.count(),
            'approved_pledges': profile.user.pledges.filter(status='approved').count(),
            'total_impact': profile.user.pledges.filter(status='approved').count() * 5.00,
            'country': profile.user.country
        })

    circle_serializer = CommunityCircleSerializer(top_circles, many=True, context={'request': request})

    return Response({
        'top_users': user_data,
        'top_circles': circle_serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def impact_stories_api(request):
    """API endpoint for impact stories"""
    approved_pledges = KarmaPledge.objects.filter(
        status='approved'
    ).select_related('user').order_by('-created_at')[:50]

    stories = []
    for pledge in approved_pledges:
        stories.append({
            'pledge_id': pledge.id,
            'user_username': pledge.user.username,
            'pledge_text': pledge.pledge_text,
            'impact_plan': pledge.impact_plan,
            'impact_type': pledge.impact_type,
            'created_at': pledge.created_at,
            'total_impact': 5.00  # $5 rebate per pledge
        })

    return Response(stories)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_metrics_api(request):
    """API endpoint for user metrics"""
    service = RenaisGinService()
    metrics = service.get_user_metrics(request.user)
    serializer = UserMetricsSerializer(metrics)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_api(request):
    """API endpoint for user statistics"""
    user = request.user
    stats = {
        'total_pledges': user.pledges.count(),
        'approved_pledges': user.pledges.filter(status='approved').count(),
        'pending_pledges': user.pledges.filter(status='pending').count(),
        'total_bottles': user.bottles.count(),
        'validations_given': user.validations_given.count(),
        'circles_joined': user.community_circles.count(),
        'circles_led': user.led_circles.count(),
    }
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_bottle_api(request, bottle_id):
    """API endpoint for bottle validation"""
    service = RenaisGinService()
    result = service.process_bottle_scan(bottle_id, request.user.id)
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_circle_api(request, circle_id):
    """API endpoint for joining a community circle"""
    service = CommunityService()
    result = service.join_community_circle(request.user, circle_id)
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_circle_api(request, circle_id):
    """API endpoint for leaving a community circle"""
    service = CommunityService()
    result = service.leave_community_circle(request.user, circle_id)
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_pledge_api(request, pledge_id):
    """API endpoint for validating a pledge"""
    approval = request.data.get('approval', False)
    comments = request.data.get('comments', '')

    service = RenaisGinService()
    result = service.validate_pledge(
        request.user,
        pledge_id,
        approval,
        comments,
        get_client_ip(request),
        request.META.get('HTTP_USER_AGENT', '')
    )
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def process_rebates_api(request):
    """API endpoint for processing rebates (admin only)"""
    from .tasks import process_rebate_payments
    result = process_rebate_payments.delay()
    return Response({'task_id': result.id, 'message': 'Rebate processing started'})


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_metrics_api(request):
    """API endpoint for updating metrics (admin only)"""
    from .tasks import update_movement_metrics
    result = update_movement_metrics.delay()
    return Response({'task_id': result.id, 'message': 'Metrics update started'})


# Utility function
def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
