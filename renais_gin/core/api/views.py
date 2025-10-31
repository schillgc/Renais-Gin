# core/api/views.py
"""
API Views for Renais Gin
REST API endpoints for mobile apps and external services
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .serializers import (
    BottleSerializer,
    PledgeSerializer,
    MetricsSerializer,
    UserProfileSerializer
)
from core.ai_services import get_ai_core
from core.models import Bottle, KarmaPledge, UserProfile
import logging

logger = logging.getLogger(__name__)


class BottleViewSet(viewsets.ModelViewSet):
    """API endpoints for bottle management"""
    queryset = Bottle.objects.all()
    serializer_class = BottleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only bottles belonging to the current user"""
        return self.queryset.filter(registered_to=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request):
        """Register a new bottle via QR code scan"""
        bottle_id = request.data.get('bottle_id')
        user_id = request.user.id

        ai_core = get_ai_core()
        result = ai_core.handle_bottle_purchase(
            user_id=str(user_id),
            bottle_data={'bottle_id': bottle_id, 'batch_id': 'default', 'date': '2023-01-01'}
        )

        return Response(result)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def details(self, request, pk=None):
        """Get detailed bottle information"""
        bottle = self.get_object()
        serializer = self.get_serializer(bottle)
        return Response(serializer.data)


class PledgeViewSet(viewsets.ModelViewSet):
    """API endpoints for pledge management"""
    queryset = KarmaPledge.objects.all()
    serializer_class = PledgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only pledges belonging to the current user"""
        return self.queryset.filter(user=self.request.user)

    def create(self, request):
        """Create a new pledge with AI validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ai_core = get_ai_core()
        validation_result = ai_core.validate_pledge(
            pledge_text=serializer.validated_data['pledge_text'],
            impact_plan=serializer.validated_data['impact_plan'],
            user_id=str(request.user.id)
        )

        if validation_result['status'] == 'rejected':
            return Response(
                {'error': validation_result['reason']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the pledge
        pledge = serializer.save(user=request.user)

        # Submit for community validation
        submission_result = ai_core.submit_community_pledge(
            user_id=str(request.user.id),
            bottle_id=serializer.validated_data['bottle_id'],
            pledge_text=serializer.validated_data['pledge_text'],
            impact_plan=serializer.validated_data['impact_plan']
        )

        response_data = serializer.data
        response_data.update(submission_result)

        logger.info("Created pledge %s for user %s", pledge.id, request.user.id)
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def validate(self, request, pk=None):
        """Validate another user's pledge"""
        pledge = self.get_object()
        approval = request.data.get('approval', False)
        comments = request.data.get('comments', '')

        ai_core = get_ai_core()
        # This would integrate with the KarmaEconomyManager
        # For now, return mock response
        return Response({
            'status': 'validated',
            'pledge_id': pk,
            'approval': approval,
            'validator': request.user.id
        })


class MetricsViewSet(viewsets.ViewSet):
    """API endpoints for movement metrics"""
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request):
        """Get overall movement metrics"""
        ai_core = get_ai_core()
        report = ai_core.generate_movement_report()

        serializer = MetricsSerializer(data=report)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def personal(self, request):
        """Get personal metrics and recommendations"""
        ai_core = get_ai_core()
        recommendations = ai_core.get_personalized_recommendations(str(request.user.id))

        return Response({
            'user_id': request.user.id,
            'recommendations': recommendations,
            'engagement_score': 0,  # Would calculate from actual data
            'impact_contribution': 0  # Would calculate from actual data
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoints for user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's profile"""
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
