"""
AI services integration for Renais Gin.

This module integrates the AI functionality from the Jupyter notebook
into the Django application.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from collections import defaultdict
from PIL import Image
import qrcode

from django.conf import settings


class BlockchainManager:
    """Manages transparent impact tracking - Mock version for demo"""

    def __init__(self):
        self.mock_mode = settings.RENAIS_SETTINGS.get('BLOCKCHAIN_MOCK_MODE', True)
        self.validation_history = {}

    def record_karma_validation(self, submission_id: str, validators: List[str], approval: bool):
        """Record karma validation on blockchain for transparency"""
        if submission_id not in self.validation_history:
            self.validation_history[submission_id] = []

        self.validation_history[submission_id].append({
            'validators': validators,
            'approval': approval,
            'timestamp': datetime.now().isoformat()
        })

        print(f"Blockchain: Recorded validation for {submission_id}")
        return {"status": "success", "mock": self.mock_mode}

    def get_validation_history(self, submission_id: str) -> List[Dict]:
        """Get validation history for a submission"""
        return self.validation_history.get(submission_id, [])


class RenaissanceBottleManager:
    """Manages the QR code and bottle tracking system"""

    def __init__(self):
        self.bottle_db = {}
        self.qr_codes = {}
        qr_code_dir = settings.MEDIA_ROOT / settings.RENAIS_SETTINGS['QR_CODE_DIR']
        os.makedirs(qr_code_dir, exist_ok=True)

    def generate_bottle_qr(self, bottle_id: str, batch_info: Dict) -> str:
        """Generate QR code for a bottle with embedded information"""
        bottle_data = {
            'bottle_id': bottle_id,
            'batch_id': batch_info['batch_id'],
            'production_date': batch_info['production_date'].isoformat() if hasattr(batch_info['production_date'],
                                                                                    'isoformat') else batch_info[
                'production_date'],
            'terroir_data': {
                'region': batch_info.get('terroir_region', ''),
                'vintage': batch_info.get('terroir_vintage', '')
            }
        }

        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(bottle_data))
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        img_path = settings.MEDIA_ROOT / settings.RENAIS_SETTINGS['QR_CODE_DIR'] / f"{bottle_id}.png"
        img.save(img_path)

        self.bottle_db[bottle_id] = bottle_data
        self.qr_codes[bottle_id] = str(img_path)

        return str(img_path)

    def process_bottle_scan(self, bottle_id: str, user_id: str) -> Dict:
        """Process when a user scans a bottle QR code"""
        if bottle_id not in self.bottle_db:
            return {"error": "Invalid bottle ID"}

        bottle_data = self.bottle_db[bottle_id]

        # Check if this bottle has already been registered
        if 'registered' in bottle_data and bottle_data['registered']:
            return {"error": "Bottle already registered"}

        # Register bottle to user
        bottle_data['registered'] = True
        bottle_data['registered_to'] = user_id
        bottle_data['registration_date'] = datetime.now().isoformat()

        return {
            "status": "success",
            "bottle_data": bottle_data,
            "karma_access": True,
            "rebate_available": True
        }


class KarmaValidationAgent:
    """AI agent for validating community pledges and stories"""

    def __init__(self):
        self.validation_threshold = settings.RENAIS_SETTINGS['COMMUNITY_VALIDATIONS_REQUIRED']
        self.community_validators = set()

    def analyze_pledge_sentiment(self, pledge_text: str) -> float:
        """Analyze the authenticity and sentiment of a pledge"""
        positive_words = [
            'plant', 'help', 'support', 'create', 'improve', 'better',
            'community', 'green', 'sustainable', 'native', 'biodiversity',
            'recycle', 'clean', 'protect', 'conserve', 'restore', 'educate',
            'volunteer', 'donate', 'partner', 'collaborate', 'organize'
        ]

        negative_words = [
            'money', 'profit', 'business', 'company', 'commercial',
            'advertisement', 'promotion', 'spam', 'fake'
        ]

        pledge_lower = pledge_text.lower()

        # Count positive words
        positive_count = sum(1 for word in positive_words if word in pledge_lower)

        # Count negative words (reduce score)
        negative_count = sum(1 for word in negative_words if word in pledge_lower)

        # Calculate word metrics
        words = pledge_text.split()
        word_count = len(words)

        if word_count == 0:
            return 0.0

        # Calculate sentence complexity (more sentences = better)
        sentence_count = max(pledge_text.count('.') + pledge_text.count('!') + pledge_text.count('?'), 1)

        # Base score from positive words
        positive_score = min(positive_count / 8.0, 1.0) * 0.6

        # Deduct for negative words
        negative_penalty = min(negative_count / 3.0, 1.0) * 0.3

        # Length score (longer pledges are generally better)
        length_score = min(word_count / 50.0, 1.0) * 0.2

        # Sentence complexity score
        complexity_score = min(sentence_count / 3.0, 1.0) * 0.2

        # Combine scores
        score = positive_score + length_score + complexity_score - negative_penalty

        # Ensure score is between 0 and 1
        return max(0.0, min(score, 1.0))

    def validate_submission(self, submission_data: Dict) -> Dict:
        """Validate a community submission"""
        sentiment_score = self.analyze_pledge_sentiment(submission_data['pledge_text'])

        threshold = settings.RENAIS_SETTINGS['AI_VALIDATION_THRESHOLD']
        review_threshold = threshold * 0.7

        if sentiment_score < review_threshold:
            return {
                "status": "rejected",
                "reason": "Pledge lacks authenticity and detail",
                "score": sentiment_score
            }
        elif sentiment_score < threshold:
            return {
                "status": "needs_review",
                "score": sentiment_score,
                "feedback": "Consider adding more specific details about your impact plan"
            }
        else:
            return {
                "status": "approved",
                "score": sentiment_score,
                "feedback": "Strong pledge with clear impact potential"
            }


class StoryCurationAgent:
    """AI agent for curating and amplifying community stories"""

    def __init__(self):
        self.story_db = []

    def add_story(self, story_text: str, metadata: Dict):
        """Add a story to the curation database"""
        self.story_db.append({"text": story_text, "metadata": metadata})

    def find_theme_clusters(self) -> List[List[Dict]]:
        """Cluster stories into thematic groups"""
        if not self.story_db:
            return []

        # Simplified clustering for demonstration
        themes = {
            'environmental': [],
            'community': [],
            'education': [],
            'other': []
        }

        for story in self.story_db:
            impact_type = story['metadata'].get('impact_type', 'other')
            themes[impact_type].append(story)

        return [stories for stories in themes.values() if stories]

    def generate_impact_report(self, timeframe_days: int = 30) -> Dict:
        """Generate impact report from stories"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)

        recent_stories = [
            s for s in self.story_db
            if s['metadata']['timestamp'] > cutoff_date
        ]

        impact_categories = defaultdict(int)
        for story in recent_stories:
            impact_categories[story['metadata'].get('impact_type', 'other')] += 1

        return dict(impact_categories)


class CommunityGrowthAgent:
    """AI agent for managing community growth and engagement"""

    def __init__(self):
        self.member_profiles = {}
        self.engagement_scores = {}
        self.circle_leaders = set()

    def track_engagement(self, user_id: str, action_type: str, value: float = 1.0):
        """Track user engagement metrics"""
        if user_id not in self.engagement_scores:
            self.engagement_scores[user_id] = defaultdict(float)

        self.engagement_scores[user_id][action_type] += value

    def identify_potential_leaders(self, min_engagement: float = 10.0) -> List[str]:
        """Identify community members with leadership potential"""
        potential_leaders = []
        for user_id, scores in self.engagement_scores.items():
            total_engagement = sum(scores.values())
            if total_engagement >= min_engagement and user_id not in self.circle_leaders:
                potential_leaders.append((user_id, total_engagement))

        return sorted(potential_leaders, key=lambda x: x[1], reverse=True)

    def form_community_circle(self, leader_id: str, location: str, max_members: int = 20):
        """Form a new community circle with identified leader"""
        if leader_id in self.circle_leaders:
            return False

        self.circle_leaders.add(leader_id)
        # Implementation would connect with actual community platform
        return True


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


class RenaissanceAICore:
    """Main AI orchestration system for Renais Gin movement"""

    def __init__(self):
        self.blockchain = BlockchainManager()
        self.karma_agent = KarmaValidationAgent()
        self.story_agent = StoryCurationAgent()
        self.community_agent = CommunityGrowthAgent()
        self.personalization_agent = PersonalizationAgent()
        self.bottle_manager = RenaissanceBottleManager()

        # Movement metrics
        self.movement_metrics = {
            'total_pledges': 0,
            'total_rebates': 0,
            'community_size': 0,
            'impact_stories': 0,
            'global_reach': defaultdict(int)
        }

    def initialize_ecosystem(self):
        """Initialize the complete Renaissance ecosystem"""
        print("Initializing Renais Gin AI Ecosystem...")

        # Load initial data and models
        self._load_initial_data()

        print("Ecosystem initialized. Ready to craft a better world.")

    def process_pledge_submission(self, user_id: str, bottle_id: str,
                                  pledge_text: str, impact_plan: str) -> Dict:
        """Process a new pledge submission"""
        # AI validation
        validation_result = self.karma_agent.validate_submission({
            'pledge_text': pledge_text,
            'impact_plan': impact_plan
        })

        return validation_result

    def classify_impact_type(self, impact_plan: str) -> str:
        """Classify impact type from text"""
        plan_lower = impact_plan.lower()

        environmental_keywords = [
            'environment', 'sustainable', 'recycle', 'planet', 'tree',
            'plant', 'green', 'eco', 'climate', 'carbon', 'biodiversity',
            'wildlife', 'nature', 'forest', 'ocean', 'cleanup'
        ]

        community_keywords = [
            'community', 'local', 'neighborhood', 'help', 'support',
            'people', 'families', 'children', 'elderly', 'homeless',
            'food', 'shelter', 'health', 'safety', 'park', 'garden'
        ]

        education_keywords = [
            'education', 'teach', 'learn', 'school', 'students',
            'children', 'youth', 'workshop', 'program', 'curriculum',
            'awareness', 'knowledge', 'skills', 'training'
        ]

        env_count = sum(1 for word in environmental_keywords if word in plan_lower)
        comm_count = sum(1 for word in community_keywords if word in plan_lower)
        edu_count = sum(1 for word in education_keywords if word in plan_lower)

        counts = {
            'environmental': env_count,
            'community': comm_count,
            'education': edu_count
        }

        # Return the category with the highest count
        max_category = max(counts, key=counts.get)

        # If no strong category, return 'other'
        return max_category if counts[max_category] > 0 else 'other'

    def _load_initial_data(self):
        """Load initial data and models"""
        # This would load ML models in production
        # For now, it's a placeholder
        pass

    def generate_movement_report(self) -> Dict:
        """Generate comprehensive movement impact report"""
        impact_categories = self.story_agent.generate_impact_report()

        return {
            'movement_metrics': self.movement_metrics,
            'impact_by_category': impact_categories,
            'community_engagement': dict(self.community_agent.engagement_scores),
            'global_reach': dict(self.movement_metrics['global_reach']),
            'timestamp': datetime.now().isoformat()
        }
