"""
API URL configuration for Renais Gin.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', api_views.UserProfileViewSet, basename='user')
router.register(r'bottles', api_views.BottleViewSet, basename='bottle')
router.register(r'pledges', api_views.KarmaPledgeViewSet, basename='pledge')
router.register(r'validations', api_views.PledgeValidationViewSet, basename='validation')
router.register(r'rebates', api_views.RebateViewSet, basename='rebate')
router.register(r'circles', api_views.CommunityCircleViewSet, basename='circle')
router.register(r'documents', api_views.UserPDFDocumentViewSet, basename='document')
router.register(r'reports', api_views.GeneratedReportViewSet, basename='report')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Authentication
    path('auth/register/', api_views.register_user_api, name='api-register'),
    path('auth/login/', api_views.login_user_api, name='api-login'),
    path('auth/logout/', api_views.logout_user_api, name='api-logout'),

    # Public endpoints
    path('metrics/', api_views.movement_metrics_api, name='api-metrics'),
    path('leaderboard/', api_views.leaderboard_api, name='api-leaderboard'),
    path('impact-stories/', api_views.impact_stories_api, name='api-impact-stories'),

    # Utility endpoints
    path('bottles/validate/<str:bottle_id>/', api_views.validate_bottle_api, name='api-validate-bottle'),
    path('circles/<int:circle_id>/join/', api_views.join_circle_api, name='api-join-circle'),
    path('circles/<int:circle_id>/leave/', api_views.leave_circle_api, name='api-leave-circle'),
    path('pledges/<int:pledge_id>/validate/', api_views.validate_pledge_api, name='api-validate-pledge'),

    # User-specific endpoints
    path('user/metrics/', api_views.user_metrics_api, name='api-user-metrics'),
    path('user/stats/', api_views.user_stats_api, name='api-user-stats'),

    # Admin endpoints
    path('admin/rebates/process/', api_views.process_rebates_api, name='api-process-rebates'),
    path('admin/metrics/update/', api_views.update_metrics_api, name='api-update-metrics'),
]
