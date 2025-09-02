import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from .models import KarmaPledge, MovementMetrics, UserProfile


class KarmaValidationService:
    """Service for validating community pledges"""

    @staticmethod
    def analyze_pledge_sentiment(pledge_text):
        """Analyze the authenticity and sentiment of a pledge"""
        positive_words = ['plant', 'help', 'support', 'create', 'improve', 'better', 'community', 'green',
                          'sustainable']
        pledge_lower = pledge_text.lower()

        # Count positive words
        positive_count = sum(1 for word in positive_words if word in pledge_lower)

        # Simple score based on positive words and length
        word_count = len(pledge_text.split())
        if word_count == 0:
            return 0.0

        score = min(positive_count / 5.0, 1.0) * 0.7 + min(word_count / 50.0, 1.0) * 0.3
        return score

    @staticmethod
    def validate_submission(pledge_text, impact_plan):
        """Validate a community submission"""
        sentiment_score = KarmaValidationService.analyze_pledge_sentiment(pledge_text)

        if sentiment_score < 0.3:
            return {"status": "rejected", "reason": "Pledge lacks authenticity"}
        elif sentiment_score < 0.6:
            return {"status": "needs_review", "score": sentiment_score}
        else:
            return {"status": "approved", "score": sentiment_score}

    @staticmethod
    def classify_impact_type(impact_plan):
        """Classify impact type from text"""
        plan_lower = impact_plan.lower()
        if any(word in plan_lower for word in ['environment', 'sustainable', 'recycle', 'planet']):
            return 'environmental'
        elif any(word in plan_lower for word in ['community', 'local', 'neighborhood', 'help']):
            return 'community'
        elif any(word in plan_lower for word in ['education', 'teach', 'learn', 'school']):
            return 'education'
        else:
            return 'other'


class StoryCurationService:
    """Service for curating and analyzing community stories"""

    @staticmethod
    def generate_impact_report(timeframe_days=30):
        """Generate impact report from stories"""
        time_threshold = datetime.now() - timedelta(days=timeframe_days)
        recent_pledges = KarmaPledge.objects.filter(timestamp__gte=time_threshold)

        impact_categories = defaultdict(int)
        for pledge in recent_pledges:
            impact_categories[pledge.impact_type] += 1

        return dict(impact_categories)


class CommunityGrowthService:
    """Service for managing community growth and engagement"""

    @staticmethod
    def identify_potential_leaders(min_engagement=10.0):
        """Identify community members with leadership potential"""
        # This would be implemented with actual engagement metrics
        # For now, return users who have submitted multiple pledges
        from django.db.models import Count
        from django.contrib.auth.models import User

        potential_leaders = User.objects.annotate(
            pledge_count=Count('karmapledge')
        ).filter(pledge_count__gte=3).exclude(
            led_circles__isnull=False
        )

        return [(user, user.pledge_count) for user in potential_leaders]


class PersonalizationService:
    """Service for personalized user experiences"""

    @staticmethod
    def generate_recommendations(user):
        """Generate personalized recommendations for user"""
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return []

        recommendations = []

        # Recommend causes based on preferences
        if hasattr(profile, 'preferences') and 'preferred_causes' in profile.preferences:
            top_causes = sorted(
                profile.preferences['preferred_causes'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            for cause, score in top_causes:
                recommendations.append({
                    'type': 'cause',
                    'value': cause,
                    'confidence': min(score / 10.0, 1.0)
                })

        return recommendations


class MovementMetricsService:
    """Service for tracking and updating movement metrics"""

    @staticmethod
    def update_metrics():
        """Update all movement metrics"""
        metrics, created = MovementMetrics.objects.get_or_create(pk=1)

        metrics.total_pledges = KarmaPledge.objects.count()
        metrics.community_size = UserProfile.objects.count()
        metrics.impact_stories = KarmaPledge.objects.filter(status='approved').count()

        # Calculate global reach
        global_reach = defaultdict(int)
        for profile in UserProfile.objects.all():
            if profile.country:
                global_reach[profile.country] += 1

        metrics.global_reach = dict(global_reach)
        metrics.save()

        return metrics
