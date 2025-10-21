# ai_agents/personalization_agent.py
from typing import List, Dict
from collections import defaultdict

class PersonalizationAgent:
    """AI agent for personalized user experiences"""

    def __init__(self):
        self.user_preferences = defaultdict(dict)

    def build_user_profile(self, user_id: str, interactions: List[Dict]):
        """Build personalized user profile based on interactions"""
        profile = {
            'preferred_causes': defaultdict(float),
            'engagement_patterns': defaultdict(float),
            'content_preferences': defaultdict(float)
        }

        for interaction in interactions:
            if interaction['type'] == 'cause_interest':
                profile['preferred_causes'][interaction['value']] += 1
            elif interaction['type'] == 'content_engagement':
                profile['content_preferences'][interaction['category']] += interaction['value']

        self.user_preferences[user_id] = profile
        return profile

    def generate_recommendations(self, user_id: str) -> List[Dict]:
        """Generate personalized recommendations for user"""
        if user_id not in self.user_preferences:
            return []

        profile = self.user_preferences[user_id]
        recommendations = []

        # Recommend causes based on preferences
        top_causes = sorted(profile['preferred_causes'].items(), key=lambda x: x[1], reverse=True)[:3]
        for cause, score in top_causes:
            recommendations.append({
                'type': 'cause',
                'value': cause,
                'confidence': min(score / 10.0, 1.0)
            })

        # Recommend content based on preferences
        top_content = sorted(profile['content_preferences'].items(), key=lambda x: x[1], reverse=True)[:2]
        for content_type, score in top_content:
            recommendations.append({
                'type': 'content',
                'value': content_type,
                'confidence': min(score / 5.0, 1.0)
            })

        return recommendations
