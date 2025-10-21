# ai_agents/karma_validation_agent.py
class KarmaValidationAgent:
    """AI agent for validating community pledges"""

    def __init__(self):
        self.positive_words = [
            'plant', 'help', 'support', 'create', 'improve', 'better',
            'community', 'green', 'sustainable', 'environment', 'local',
            'education', 'teach', 'learn', 'protect', 'conserve'
        ]

    def analyze_pledge_sentiment(self, pledge_text: str) -> float:
        """Analyze pledge authenticity and sentiment"""
        if not pledge_text:
            return 0.0

        pledge_lower = pledge_text.lower()

        # Count positive words
        positive_count = sum(1 for word in self.positive_words if word in pledge_lower)

        # Calculate score based on positive words and text length
        word_count = len(pledge_text.split())
        if word_count == 0:
            return 0.0

        score = min(positive_count / 5.0, 1.0) * 0.7 + min(word_count / 50.0, 1.0) * 0.3
        return round(score, 2)

    def validate_submission(self, submission_data: Dict) -> Dict:
        """Validate a community submission"""
        sentiment_score = self.analyze_pledge_sentiment(submission_data['pledge'])

        if sentiment_score < 0.3:
            return {
                "status": "rejected",
                "reason": "Pledge lacks authenticity or specific action",
                "score": sentiment_score
            }
        elif sentiment_score < 0.6:
            return {
                "status": "needs_review",
                "score": sentiment_score,
                "feedback": "Consider making your pledge more specific and actionable"
            }
        else:
            return {
                "status": "approved",
                "score": sentiment_score,
                "feedback": "Strong pledge with clear impact potential"
            }

