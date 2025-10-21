"""
Tests for AI services integration
"""

from django.test import TestCase
from django.contrib.auth.models import User
from core.ai_services import (
    RenaissanceAICore,
    KarmaValidationAgent,
    BlockchainManager,
    RenaissanceBottleManager
)


class AIServicesTestCase(TestCase):
    """Test cases for AI services"""

    def setUp(self):
        self.ai_core = RenaissanceAICore()
        self.karma_agent = KarmaValidationAgent()
        self.blockchain = BlockchainManager()
        self.bottle_manager = RenaissanceBottleManager()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@renaisgin.com',
            password='testpass123'
        )

    def test_pledge_validation_high_quality(self):
        """Test validation of a high-quality pledge"""
        pledge_text = (
            "I pledge to use this $5 rebate to plant 15 native oak trees "
            "in partnership with our city's urban forestry program. These trees "
            "will help combat climate change, improve air quality, and provide "
            "habitat for local wildlife in our community park."
        )
        impact_plan = (
            "I will coordinate with the Parks Department to schedule the planting "
            "for next month's community green day. I've already identified a local "
            "nursery that specializes in native species and will organize volunteers "
            "from my neighborhood association to help with the planting."
        )

        result = self.karma_agent.validate_submission({
            'pledge': pledge_text,
            'impact_plan': impact_plan,
            'user_id': str(self.user.id)
        })

        self.assertIn('status', result)
        self.assertIn('score', result)
        self.assertGreater(result['score'], 0.5)

    def test_pledge_validation_low_quality(self):
        """Test validation of a low-quality pledge"""
        pledge_text = "I will do something good."
        impact_plan = "I'll figure it out."

        result = self.karma_agent.validate_submission({
            'pledge': pledge_text,
            'impact_plan': impact_plan,
            'user_id': str(self.user.id)
        })

        self.assertIn('status', result)
        self.assertIn('score', result)
        self.assertLess(result['score'], 0.5)

    def test_bottle_registration_flow(self):
        """Test the complete bottle registration flow"""
        bottle_data = {
            'bottle_id': 'TEST_BOTTLE_001',
            'batch_id': 'BATCH_2023_001',
            'date': '2023-10-01',
            'terroir': {
                'region': 'Chablis',
                'vintage': '2022'
            }
        }

        # Generate QR code
        qr_path = self.bottle_manager.generate_bottle_qr(
            bottle_data['bottle_id'],
            bottle_data
        )

        self.assertIsNotNone(qr_path)
        self.assertIn('TEST_BOTTLE_001', qr_path)

        # Process bottle scan
        result = self.bottle_manager.process_bottle_scan(
            bottle_data['bottle_id'],
            str(self.user.id)
        )

        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['karma_access'])

    def test_blockchain_recording(self):
        """Test blockchain validation recording"""
        submission_id = 'test_submission_123'
        validators = ['validator_1', 'validator_2']
        approval = True

        result = self.blockchain.record_karma_validation(
            submission_id,
            validators,
            approval
        )

        self.assertEqual(result['status'], 'success')

        # Check history
        history = self.blockchain.get_validation_history(submission_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['approval'], approval)

    def test_ai_core_integration(self):
        """Test the complete AI core integration"""
        # Test new member processing
        user_data = {
            'user_id': str(self.user.id),
            'name': 'Test User',
            'country': 'USA',
            'email': 'test@renaisgin.com'
        }

        processed_id = self.ai_core.process_new_member(user_data)
        self.assertEqual(processed_id, str(self.user.id))

        # Test pledge validation
        pledge_text = "I pledge to organize a community recycling drive."
        impact_plan = "I'll work with local businesses to set up collection points."

        validation_result = self.ai_core.validate_pledge(
            pledge_text,
            impact_plan,
            str(self.user.id)
        )

        self.assertIn('status', validation_result)

        # Test movement report generation
        report = self.ai_core.generate_movement_report()
        self.assertIn('movement_metrics', report)
        self.assertIn('global_reach', report)

    def test_personalized_recommendations(self):
        """Test personalized recommendation generation"""
        # Build user profile through interactions
        interactions = [
            {'type': 'cause_interest', 'value': 'environmental'},
            {'type': 'cause_interest', 'value': 'environmental'},
            {'type': 'cause_interest', 'value': 'community'},
            {'type': 'content_engagement', 'category': 'tree_planting', 'value': 2},
            {'type': 'content_engagement', 'category': 'cleanup_events', 'value': 1},
        ]

        self.ai_core.personalization_agent.build_user_profile(
            str(self.user.id),
            interactions
        )

        recommendations = self.ai_core.get_personalized_recommendations(
            str(self.user.id)
        )

        self.assertIsInstance(recommendations, list)

        # Environmental should be top recommendation
        if recommendations:
            top_recommendation = recommendations[0]
            self.assertIn('type', top_recommendation)
            self.assertIn('value', top_recommendation)
            self.assertIn('confidence', top_recommendation)


class MockAITestCase(TestCase):
    """Test AI services in mock mode"""

    def setUp(self):
        # Force mock mode
        import os
        os.environ['AI_MOCK_MODE'] = 'True'

        from core.ai_services import RenaissanceAICore
        self.ai_core = RenaissanceAICore()

    def test_mock_validation(self):
        """Test AI validation in mock mode"""
        result = self.ai_core.validate_pledge(
            "Test pledge",
            "Test impact plan",
            "test_user"
        )

        self.assertIn('status', result)
        # In mock mode, should always return a result
        self.assertIn(result['status'], ['approved', 'needs_review', 'rejected'])
