# ai_agents/story_curation_agent.py
from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta

class StoryCurationAgent:
    """AI agent for curating and amplifying community stories"""

    def __init__(self):
        self.story_db = []

    def add_story(self, story_text: str, metadata: Dict):
        """Add a story to the curation database"""
        self.story_db.append({"text": story_text, "metadata": metadata})

    def find_theme_clusters(self) -> List[List[Dict]]:
        """Cluster stories into thematic groups (simplified for demo)"""
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
        recent_stories = [s for s in self.story_db if
                         datetime.now() - s['metadata']['timestamp'] < timedelta(days=timeframe_days)]

        impact_categories = defaultdict(int)
        for story in recent_stories:
            impact_categories[story['metadata'].get('impact_type', 'other')] += 1

        return dict(impact_categories)
