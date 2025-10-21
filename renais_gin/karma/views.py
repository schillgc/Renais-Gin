from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from .models import KarmaPledge, KarmaValidation, KarmaRebate
from .serializers import (
    KarmaPledgeSerializer, KarmaPledgeCreateSerializer,
    KarmaValidationSerializer, KarmaRebateSerializer
)


class KarmaPledgeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return KarmaPledgeCreateSerializer
        return KarmaPledgeSerializer

    def get_queryset(self):
        return KarmaPledge.objects.filter(user=self.request.user).select_related('bottle')

    def perform_create(self, serializer):
        serializer.save()


class KarmaPledgeDetailView(generics.RetrieveAPIView):
    serializer_class = KarmaPledgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'submission_id'
    lookup_url_kwarg = 'submission_id'

    def get_queryset(self):
        return KarmaPledge.objects.filter(user=self.request.user)


class PledgeValidationListView(generics.ListAPIView):
    """List pledges available for validation by the current user"""
    serializer_class = KarmaPledgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get pledges that need validation and haven't been validated by current user
        validated_pledge_ids = KarmaValidation.objects.filter(
            validator=self.request.user
        ).values_list('pledge_id', flat=True)

        return KarmaPledge.objects.filter(
            status=KarmaPledge.STATUS_PENDING
        ).exclude(
            Q(user=self.request.user) | Q(id__in=validated_pledge_ids)
        ).select_related('user', 'bottle')[:10]  # Limit to 10 for performance


class KarmaValidationCreateView(generics.CreateAPIView):
    serializer_class = KarmaValidationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Simplified implementation for now
        return Response({
            'message': 'Validation endpoint - implementation pending'
        }, status=status.HTTP_200_OK)


class RebateListView(generics.ListAPIView):
    serializer_class = KarmaRebateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KarmaRebate.objects.filter(user=self.request.user).select_related('pledge')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def karma_dashboard(request):
    """Comprehensive karma dashboard data"""
    user = request.user
    profile = user.profile

    # Pledge statistics
    total_pledges = KarmaPledge.objects.filter(user=user).count()
    approved_pledges = KarmaPledge.objects.filter(user=user, status=KarmaPledge.STATUS_APPROVED).count()
    pending_pledges = KarmaPledge.objects.filter(user=user, status=KarmaPledge.STATUS_PENDING).count()

    # Validation statistics
    validations_given = KarmaValidation.objects.filter(validator=user).count()
    positive_validations = KarmaValidation.objects.filter(validator=user, approval=True).count()

    # Rebate statistics
    total_rebates = KarmaRebate.objects.filter(user=user).count()
    processed_rebates = KarmaRebate.objects.filter(user=user, status=KarmaRebate.STATUS_PROCESSED).count()

    dashboard_data = {
        'user_stats': {
            'karma_score': user.karma_score,
            'total_pledges': total_pledges,
            'approved_pledges': approved_pledges,
            'pending_pledges': pending_pledges,
            'total_rebates_earned': float(profile.total_rebates),
        },
        'community_engagement': {
            'validations_given': validations_given,
            'positive_validations': positive_validations,
            'validation_accuracy': round(positive_validations / validations_given * 100, 1) if validations_given else 0,
        },
        'rebate_status': {
            'total_rebates': total_rebates,
            'processed_rebates': processed_rebates,
            'pending_rebates': total_rebates - processed_rebates,
        }
    }

    return Response(dashboard_data)
