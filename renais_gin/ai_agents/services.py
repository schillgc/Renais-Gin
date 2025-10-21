# ai_agents/services.py
from typing import Dict, List
from .karma_validation_agent import KarmaValidationAgent
from .story_curation_agent import StoryCurationAgent
from .personalization_agent import PersonalizationAgent


class AIService:
    """Main AI service orchestrator"""

    def __init__(self):
        self.karma_agent = KarmaValidationAgent()
        self.story_agent = StoryCurationAgent()
        self.personalization_agent = PersonalizationAgent()

    def validate_pledge(self, pledge_text: str, impact_plan: str) -> Dict:
        """Validate a karma pledge using AI"""
        return self.karma_agent.validate_submission({
            'pledge': pledge_text,
            'impact_plan': impact_plan
        })

    def curate_story(self, story_text: str, metadata: Dict) -> Dict:
        """Curate and categorize a community story"""
        return self.story_agent.process_story(story_text, metadata)

    def get_recommendations(self, user_id: str) -> List[Dict]:
        """Get personalized recommendations for user"""
        return self.personalization_agent.generate_recommendations(user_id)
