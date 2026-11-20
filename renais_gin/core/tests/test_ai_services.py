"""
Tests for the Renais Gin AI services integration.

These tests exercise the service interfaces that currently exist in
core.ai_services and use the project's configured custom user model.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.ai_services import (
    BlockchainManager,
    KarmaValidationAgent,
    RenaissanceAICore,
    RenaissanceBottleManager,
)


class AIServicesTestCase(TestCase):
    """Test cases for the implemented AI services."""

    def setUp(self):
        self.ai_core = RenaissanceAICore()
        self.karma_agent = KarmaValidationAgent()
        self.blockchain = BlockchainManager()
        self.bottle_manager = RenaissanceBottleManager()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@renaisgin.com",
            password="testpass123",
        )

    def test_pledge_validation_high_quality(self):
        """A specific, actionable pledge should receive a meaningful score."""
        pledge_text = (
            "I pledge to plant 15 native oak trees in partnership with our "
            "city's urban forestry program. These trees will help combat climate "
            "change, improve air quality, and provide habitat for local wildlife "
            "in our community park."
        )
        impact_plan = (
            "I will coordinate with the Parks Department to schedule the planting "
            "for next month's community green day. I have identified a local "
            "nursery that specializes in native species and will organize "
            "volunteers from my neighborhood association."
        )

        result = self.karma_agent.validate_submission(
            {
                "pledge_text": pledge_text,
                "impact_plan": impact_plan,
                "user_id": str(self.user.pk),
            }
        )

        self.assertIn("status", result)
        self.assertIn("score", result)
        self.assertGreater(result["score"], 0.5)

    def test_pledge_validation_low_quality(self):
        """A vague pledge should score below the meaningful-pledge threshold."""
        result = self.karma_agent.validate_submission(
            {
                "pledge_text": "I will do something good.",
                "impact_plan": "I will figure it out.",
                "user_id": str(self.user.pk),
            }
        )

        self.assertIn("status", result)
        self.assertIn("score", result)
        self.assertLess(result["score"], 0.5)

    def test_bottle_qr_generation_and_scan(self):
        """QR generation should register the in-memory bottle for later scans."""
        bottle_data = {
            "bottle_id": "TEST_BOTTLE_001",
            "batch_id": "BATCH_2023_001",
            "production_date": "2023-10-01",
            "terroir_region": "Chablis",
            "terroir_vintage": "2022",
        }

        qr_path = self.bottle_manager.generate_bottle_qr(
            bottle_data["bottle_id"],
            bottle_data,
        )

        self.assertIsNotNone(qr_path)
        self.assertIn("TEST_BOTTLE_001", qr_path)

        result = self.bottle_manager.process_bottle_scan(
            bottle_data["bottle_id"],
            str(self.user.pk),
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["karma_access"])
        self.assertEqual(result["bottle_data"]["batch_id"], "BATCH_2023_001")

    def test_blockchain_recording(self):
        """The mock blockchain manager should retain its validation history."""
        submission_id = "test_submission_123"
        validators = ["validator_1", "validator_2"]
        approval = True

        result = self.blockchain.record_karma_validation(
            submission_id,
            validators,
            approval,
        )

        self.assertEqual(result["status"], "success")
        history = self.blockchain.get_validation_history(submission_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["approval"], approval)
        self.assertEqual(history[0]["validators"], validators)

    def test_ai_core_integration(self):
        """The AI core should validate pledges and produce movement reports."""
        pledge_text = "I pledge to organize a community recycling drive."
        impact_plan = (
            "I will work with local businesses and neighborhood volunteers "
            "to establish recycling collection points."
        )

        validation_result = self.ai_core.process_pledge_submission(
            str(self.user.pk),
            "TEST_BOTTLE_001",
            pledge_text,
            impact_plan,
        )
        self.assertIn(
            validation_result["status"],
            {"approved", "needs_review", "rejected"},
        )

        self.assertEqual(
            self.ai_core.classify_impact_type(impact_plan),
            "environmental",
        )

        report = self.ai_core.generate_movement_report()
        self.assertIn("movement_metrics", report)
        self.assertIn("global_reach", report)

    def test_personalized_recommendations(self):
        """The personalization agent should rank the user's stated interests."""
        user_id = str(self.user.pk)
        interactions = [
            {"type": "cause_interest", "value": "environmental"},
            {"type": "cause_interest", "value": "environmental"},
            {"type": "cause_interest", "value": "community"},
            {"type": "content_engagement", "category": "tree_planting", "value": 2},
            {"type": "content_engagement", "category": "cleanup_events", "value": 1},
        ]

        self.ai_core.personalization_agent.build_user_profile(
            user_id,
            interactions,
        )
        recommendations = (
            self.ai_core.personalization_agent.generate_recommendations(user_id)
        )

        self.assertIsInstance(recommendations, list)
        self.assertTrue(recommendations)
        self.assertEqual(recommendations[0]["type"], "cause")
        self.assertEqual(recommendations[0]["value"], "environmental")
        self.assertIn("confidence", recommendations[0])


class LocalAIServicesTestCase(TestCase):
    """The deterministic local pledge validator should not require API credentials."""

    def setUp(self):
        self.ai_core = RenaissanceAICore()

    def test_local_validation_returns_a_supported_result(self):
        result = self.ai_core.process_pledge_submission(
            "test_user",
            "TEST_BOTTLE_002",
            "I pledge to plant native trees and support my community.",
            "I will organize volunteers to plant trees in a local park.",
        )

        self.assertIn("status", result)
        self.assertIn("score", result)
        self.assertIn(result["status"], {"approved", "needs_review", "rejected"})
