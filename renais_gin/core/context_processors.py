"""
Context processors for Renais Gin core application.
"""

from django.conf import settings
from .services import RenaisGinService


def movement_metrics(request):
    """
    Add movement metrics to template context.
    """
    if not request.path.startswith('/admin/'):  # Don't load in admin
        try:
            service = RenaisGinService()
            metrics = service.get_movement_metrics()

            # Format numbers for display
            formatted_metrics = {
                'total_community': _format_number(metrics.get('total_community', 0)),
                'total_bottles': _format_number(metrics.get('total_bottles', 0)),
                'total_pledges': _format_number(metrics.get('total_pledges', 0)),
                'approved_pledges': _format_number(metrics.get('approved_pledges', 0)),
                'total_rebates': _format_number(metrics.get('total_rebates', 0)),
                'total_impact': _format_currency(metrics.get('total_impact', 0)),
                'active_circles': _format_number(metrics.get('active_circles', 0)),
                'total_circle_members': _format_number(metrics.get('total_circle_members', 0)),
                'impact_by_category': metrics.get('impact_by_category', {}),
                'raw_metrics': metrics,  # Include raw data for charts
            }

            return {
                'movement_metrics': formatted_metrics,
            }
        except Exception as e:
            # Return empty metrics on error
            return {
                'movement_metrics': {
                    'total_community': '0',
                    'total_bottles': '0',
                    'total_pledges': '0',
                    'approved_pledges': '0',
                    'total_rebates': '0',
                    'total_impact': '$0',
                    'active_circles': '0',
                    'total_circle_members': '0',
                    'impact_by_category': {},
                }
            }
    return {}


def user_context(request):
    """
    Add user-specific context to templates.
    """
    context = {}

    if request.user.is_authenticated:
        try:
            service = RenaisGinService()
            user_metrics = service.get_user_metrics(request.user)

            # Format user metrics for display
            formatted_metrics = {
                'total_pledges': _format_number(user_metrics.get('total_pledges', 0)),
                'approved_pledges': _format_number(user_metrics.get('approved_pledges', 0)),
                'pending_pledges': _format_number(user_metrics.get('pending_pledges', 0)),
                'total_bottles': _format_number(user_metrics.get('total_bottles', 0)),
                'validations_given': _format_number(user_metrics.get('validations_given', 0)),
                'engagement_score': _format_number(user_metrics.get('engagement_score', 0)),
                'karma_score': _format_number(user_metrics.get('karma_score', 1)),
                'total_impact': _format_currency(user_metrics.get('total_impact', 0)),
                'preferred_causes': user_metrics.get('preferred_causes', []),
                'member_since': user_metrics.get('member_since', ''),
                'raw_metrics': user_metrics,  # Include raw data
            }

            context['user_metrics'] = formatted_metrics

            # Add user profile if exists
            if hasattr(request.user, 'profile'):
                context['user_profile'] = request.user.profile

            # Add notifications count (simplified)
            from .models import KarmaPledge
            pending_pledges_count = KarmaPledge.objects.filter(
                user=request.user,
                status='pending'
            ).count()
            context['pending_pledges_count'] = pending_pledges_count

            # Add validation opportunities count
            validation_opportunities = KarmaPledge.objects.filter(
                status='pending'
            ).exclude(
                user=request.user
            ).exclude(
                validations__validator=request.user
            ).count()
            context['validation_opportunities'] = validation_opportunities

        except Exception as e:
            # Return empty metrics on error
            context['user_metrics'] = {
                'total_pledges': '0',
                'approved_pledges': '0',
                'pending_pledges': '0',
                'total_bottles': '0',
                'validations_given': '0',
                'engagement_score': '0',
                'karma_score': '0',
                'total_impact': '$0',
                'preferred_causes': [],
                'member_since': '',
            }
            context['pending_pledges_count'] = 0
            context['validation_opportunities'] = 0

    return context


def renais_settings(request):
    """
    Add Renais Gin settings to template context.
    """
    return {
        'renais_settings': settings.RENAIS_SETTINGS,
        'debug': settings.DEBUG,
        'site_name': 'Renais Gin',
        'site_description': 'Craft Your Perfect World',
    }


def navigation_context(request):
    """
    Add navigation context for active menu items.
    """
    path = request.path

    # Determine active section based on URL
    active_section = 'home'
    if path.startswith('/dashboard'):
        active_section = 'dashboard'
    elif path.startswith('/bottles'):
        active_section = 'bottles'
    elif path.startswith('/karma'):
        active_section = 'karma'
    elif path.startswith('/community'):
        active_section = 'community'
    elif path.startswith('/impact'):
        active_section = 'impact'
    elif path.startswith('/documents'):
        active_section = 'documents'
    elif path.startswith('/profile'):
        active_section = 'profile'

    return {
        'active_section': active_section,
        'current_path': path,
    }


def feature_flags(request):
    """
    Add feature flags for gradual rollout of features.
    """
    return {
        'feature_flags': {
            'community_circles': True,
            'impact_stories': True,
            'leaderboard': True,
            'pdf_uploads': True,
            'ai_validation': True,
            'rebate_processing': True,
            'advanced_metrics': True,
        }
    }


# Utility functions for formatting
def _format_number(number):
    """Format numbers for display with K/M suffixes"""
    if isinstance(number, (int, float)):
        if number >= 1000000:
            return f"{number / 1000000:.1f}M"
        elif number >= 1000:
            return f"{number / 1000:.1f}K"
        else:
            return str(number)
    return str(number)


def _format_currency(amount):
    """Format currency amounts"""
    if isinstance(amount, (int, float)):
        return f"${amount:,.2f}"
    return f"${amount}"


def _format_percentage(decimal):
    """Format percentages"""
    if isinstance(decimal, (int, float)):
        return f"{decimal * 100:.1f}%"
    return "0%"
