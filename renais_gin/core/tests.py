"""
Tests for Renais Gin core application.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    UserProfile, Bottle, KarmaPledge, PledgeValidation,
    Rebate, CommunityCircle
)
from .services import RenaisGinService, CommunityService
from .forms import (
    PledgeForm, CommunityCircleForm, UserProfileForm,
    ValidationForm, BottleRegistrationForm, PDFUploadForm
)


class ModelTests(TestCase):
    """
    Test cases for database models.
    """

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@renaisgin.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@renaisgin.com',
            password='otherpass123'
        )

        self.bottle = Bottle.objects.create(
            bottle_id='TEST001',
            batch_id='BATCH001',
            production_date='2023-01-01',
            terroir_region='Chablis',
            terroir_vintage='2022'
        )

    def test_user_profile_creation(self):
        """Test that user profile is created automatically"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.karma_score, 0.0)
        self.assertEqual(self.user.profile.engagement_score, 0)

    def test_bottle_creation(self):
        """Test bottle creation and QR code generation"""
        self.assertEqual(self.bottle.bottle_id, 'TEST001')
        self.assertFalse(self.bottle.registered)
        self.assertIsNone(self.bottle.registered_to)

        # Test QR code generation on save
        self.bottle.save()
        self.assertIsNotNone(self.bottle.qr_code)

    def test_bottle_registration(self):
        """Test bottle registration"""
        self.bottle.registered = True
        self.bottle.registered_to = self.user
        self.bottle.registration_date = timezone.now()
        self.bottle.status = 'registered'
        self.bottle.save()

        self.assertTrue(self.bottle.registered)
        self.assertEqual(self.bottle.registered_to, self.user)
        self.assertEqual(self.bottle.status, 'registered')

    def test_bottle_can_make_pledge(self):
        """Test bottle pledge eligibility"""
        # Unregistered bottle cannot make pledge
        self.assertFalse(self.bottle.can_make_pledge())

        # Registered bottle can make pledge
        self.bottle.registered = True
        self.bottle.registered_to = self.user
        self.bottle.status = 'registered'
        self.bottle.save()

        self.assertTrue(self.bottle.can_make_pledge())

        # Bottle with existing pledge cannot make another
        pledge = KarmaPledge.objects.create(
            user=self.user,
            bottle=self.bottle,
            pledge_text='Test pledge',
            impact_plan='Test impact plan'
        )
        self.assertFalse(self.bottle.can_make_pledge())

    def test_karma_pledge_creation(self):
        """Test karma pledge creation"""
        pledge = KarmaPledge.objects.create(
            user=self.user,
            bottle=self.bottle,
            pledge_text='I pledge to plant trees in my community',
            impact_plan='I will organize monthly tree planting events',
            impact_type='environmental',
            status='pending'
        )

        self.assertEqual(pledge.user, self.user)
        self.assertEqual(pledge.bottle, self.bottle)
        self.assertEqual(pledge.impact_type, 'environmental')
        self.assertEqual(pledge.status, 'pending')
        self.assertIsNotNone(pledge.submission_id)

    def test_pledge_validation(self):
        """Test pledge validation system"""
        pledge = KarmaPledge.objects.create(
            user=self.user,
            bottle=self.bottle,
            pledge_text='Test pledge',
            impact_plan='Test plan'
        )

        # Create validation
        validation = PledgeValidation.objects.create(
            pledge=pledge,
            validator=self.other_user,
            approved=True,
            comments='Great pledge!'
        )

        self.assertEqual(validation.pledge, pledge)
        self.assertEqual(validation.validator, self.other_user)
        self.assertTrue(validation.approved)
        self.assertEqual(validation.comments, 'Great pledge!')

    def test_community_circle_creation(self):
        """Test community circle creation"""
        circle = CommunityCircle.objects.create(
            name='Test Circle',
            leader=self.user,
            location='Test City',
            description='A test community circle'
        )

        self.assertEqual(circle.name, 'Test Circle')
        self.assertEqual(circle.leader, self.user)
        self.assertEqual(circle.location, 'Test City')
        self.assertTrue(circle.is_active)

        # Test member management
        circle.add_member(self.other_user)
        self.assertTrue(circle.members.filter(id=self.other_user.id).exists())
        self.assertEqual(circle.member_count, 2)  # leader + 1 member

        circle.remove_member(self.other_user)
        self.assertFalse(circle.members.filter(id=self.other_user.id).exists())
        self.assertEqual(circle.member_count, 1)  # just leader


class ServiceTests(TestCase):
    """
    Test cases for business logic services.
    """

    def setUp(self):
        """Set up test data for services"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@renaisgin.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@renaisgin.com',
            password='otherpass123'
        )

        self.bottle = Bottle.objects.create(
            bottle_id='TEST001',
            batch_id='BATCH001',
            production_date='2023-01-01',
            terroir_region='Chablis',
            terroir_vintage='2022'
        )

        self.service = RenaisGinService()
        self.community_service = CommunityService()

    def test_register_bottle(self):
        """Test bottle registration service"""
        bottle_data = {
            'bottle_id': 'TEST001',
            'batch_id': 'BATCH001',
            'production_date': '2023-01-01',
        }

        result = self.service.register_bottle(bottle_data, self.user)

        self.assertTrue(result['success'])
        self.assertEqual(result['bottle'].registered_to, self.user)
        self.assertTrue(result['bottle'].registered)

        # Test duplicate registration
        result = self.service.register_bottle(bottle_data, self.user)
        self.assertFalse(result['success'])
        self.assertIn('already registered', result['error'])

    def test_submit_pledge(self):
        """Test pledge submission service"""
        # First register the bottle
        bottle_data = {'bottle_id': 'TEST001', 'batch_id': 'BATCH001', 'production_date': '2023-01-01'}
        self.service.register_bottle(bottle_data, self.user)

        # Submit pledge
        result = self.service.submit_pledge(
            self.user,
            'TEST001',
            'I pledge to clean up local parks',
            'I will organize weekly cleanup events with my community'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['pledge'].user, self.user)
        self.assertEqual(result['pledge'].bottle, self.bottle)
        self.assertIn('ai_validation', result)

    def test_validate_pledge(self):
        """Test pledge validation service"""
        # Create a pledge
        bottle_data = {'bottle_id': 'TEST001', 'batch_id': 'BATCH001', 'production_date': '2023-01-01'}
        self.service.register_bottle(bottle_data, self.user)

        pledge_result = self.service.submit_pledge(
            self.user,
            'TEST001',
            'Test pledge',
            'Test impact plan'
        )
        pledge = pledge_result['pledge']

        # Validate the pledge
        result = self.service.validate_pledge(
            self.other_user,
            pledge.id,
            True,
            'Great pledge!'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['validation'].validator, self.other_user)
        self.assertTrue(result['validation'].approved)

        # Test self-validation prevention
        result = self.service.validate_pledge(
            self.user,
            pledge.id,
            True,
            'Should fail'
        )
        self.assertFalse(result['success'])
        self.assertIn('your own pledge', result['error'])

    def test_user_metrics(self):
        """Test user metrics calculation"""
        metrics = self.service.get_user_metrics(self.user)

        self.assertEqual(metrics['total_pledges'], 0)
        self.assertEqual(metrics['approved_pledges'], 0)
        self.assertEqual(metrics['total_bottles'], 0)
        self.assertEqual(metrics['engagement_score'], 0)
        self.assertEqual(metrics['total_impact'], 0.0)

    def test_movement_metrics(self):
        """Test global movement metrics calculation"""
        metrics = self.service.get_movement_metrics()

        self.assertIn('total_community', metrics)
        self.assertIn('total_bottles', metrics)
        self.assertIn('total_pledges', metrics)
        self.assertIn('approved_pledges', metrics)
        self.assertIn('impact_by_category', metrics)

    def test_create_community_circle(self):
        """Test community circle creation service"""
        result = self.community_service.create_community_circle(
            'Test Circle',
            'Test City',
            self.user,
            'A test circle',
            ['environmental', 'community']
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['circle'].name, 'Test Circle')
        self.assertEqual(result['circle'].leader, self.user)

        # Test duplicate circle leadership prevention
        result = self.community_service.create_community_circle(
            'Another Circle',
            'Another City',
            self.user,
            'Should fail'
        )
        self.assertFalse(result['success'])
        self.assertIn('already lead', result['error'])

    def test_join_community_circle(self):
        """Test joining community circles"""
        # Create a circle
        circle_result = self.community_service.create_community_circle(
            'Test Circle',
            'Test City',
            self.user
        )
        circle = circle_result['circle']

        # Join the circle
        result = self.community_service.join_community_circle(
            self.other_user,
            circle.id
        )

        self.assertTrue(result['success'])
        self.assertTrue(circle.members.filter(id=self.other_user.id).exists())

        # Test duplicate join prevention
        result = self.community_service.join_community_circle(
            self.other_user,
            circle.id
        )
        self.assertFalse(result['success'])
        self.assertIn('already a member', result['error'])


class FormTests(TestCase):
    """
    Test cases for form validation.
    """

    def setUp(self):
        """Set up test data for forms"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@renaisgin.com',
            password='testpass123'
        )

    def test_pledge_form_valid(self):
        """Test valid pledge form data"""
        form_data = {
            'pledge_text': 'I pledge to plant 100 trees in my community this year',
            'impact_plan': 'I will organize monthly tree planting events and partner with local nurseries',
            'impact_type': 'environmental'
        }
        form = PledgeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_pledge_form_invalid(self):
        """Test invalid pledge form data"""
        # Too short
        form_data = {
            'pledge_text': 'Short',
            'impact_plan': 'Also short',
            'impact_type': 'environmental'
        }
        form = PledgeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pledge_text', form.errors)
        self.assertIn('impact_plan', form.errors)

    def test_community_circle_form_valid(self):
        """Test valid community circle form data"""
        form_data = {
            'name': 'Test Community Circle',
            'location': 'Test City, Country',
            'description': 'A circle dedicated to environmental conservation and community building',
            'focus_areas': ['environmental', 'community']
        }
        form = CommunityCircleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_validation_form_valid(self):
        """Test valid validation form data"""
        form_data = {
            'approval': True,
            'comments': 'This is a well-thought-out pledge with clear impact potential.'
        }
        form = ValidationForm(data=form_data)
        self.assertTrue(form.is_valid())


class ViewTests(TestCase):
    """
    Test cases for views and URL routing.
    """

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@renaisgin.com',
            password='testpass123'
        )

    def test_home_view(self):
        """Test home page view"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_dashboard_authentication(self):
        """Test dashboard requires authentication"""
        # Unauthenticated access should redirect to login
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('login', response.url)

        # Authenticated access should work
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_bottle_views_authentication(self):
        """Test bottle-related views require authentication"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('core:bottles'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('core:register_bottle'))
        self.assertEqual(response.status_code, 200)

    def test_api_endpoints(self):
        """Test API endpoints"""
        # Public API endpoints should work without authentication
        response = self.client.get('/api/v1/metrics/')
        self.assertEqual(response.status_code, 200)

        # Protected API endpoints should require authentication
        response = self.client.get('/api/v1/user/metrics/')
        self.assertEqual(response.status_code, 403)  # Forbidden


class IntegrationTests(TestCase):
    """
    Integration tests for complete workflows.
    """

    def setUp(self):
        """Set up test data for integration tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@renaisgin.com',
            password='testpass123'
        )
        self.validator1 = User.objects.create_user(
            username='validator1',
            email='validator1@renaisgin.com',
            password='valpass123'
        )
        self.validator2 = User.objects.create_user(
            username='validator2',
            email='validator2@renaisgin.com',
            password='valpass123'
        )
        self.validator3 = User.objects.create_user(
            username='validator3',
            email='validator3@renaisgin.com',
            password='valpass123'
        )

        self.bottle = Bottle.objects.create(
            bottle_id='TEST001',
            batch_id='BATCH001',
            production_date='2023-01-01',
            terroir_region='Chablis',
            terroir_vintage='2022'
        )

        self.service = RenaisGinService()

    def test_complete_pledge_workflow(self):
        """Test complete pledge workflow from registration to approval"""
        # 1. Register bottle
        bottle_data = {'bottle_id': 'TEST001', 'batch_id': 'BATCH001', 'production_date': '2023-01-01'}
        reg_result = self.service.register_bottle(bottle_data, self.user)
        self.assertTrue(reg_result['success'])

        # 2. Submit pledge
        pledge_result = self.service.submit_pledge(
            self.user,
            'TEST001',
            'I pledge to organize community cleanups and plant native species',
            'I will partner with local organizations and schedule monthly events'
        )
        self.assertTrue(pledge_result['success'])
        pledge = pledge_result['pledge']
        self.assertEqual(pledge.status, 'pending')

        # 3. Multiple validations
        val1_result = self.service.validate_pledge(self.validator1, pledge.id, True, 'Great initiative!')
        self.assertTrue(val1_result['success'])

        val2_result = self.service.validate_pledge(self.validator2, pledge.id, True, 'Well planned!')
        self.assertTrue(val2_result['success'])

        # 4. Third validation should trigger approval
        val3_result = self.service.validate_pledge(self.validator3, pledge.id, True, 'Approved!')
        self.assertTrue(val3_result['success'])

        # Refresh pledge from database
        pledge.refresh_from_db()
        self.assertEqual(pledge.status, 'approved')

        # 5. Check that rebate was created
        self.assertTrue(hasattr(pledge, 'rebate'))
        self.assertEqual(pledge.rebate.amount, 5.00)

    def test_community_circle_workflow(self):
        """Test complete community circle workflow"""
        community_service = CommunityService()

        # 1. Create circle
        create_result = community_service.create_community_circle(
            'Eco Warriors',
            'Portland, OR',
            self.user,
            'Focused on environmental conservation and sustainability',
            ['environmental', 'education']
        )
        self.assertTrue(create_result['success'])
        circle = create_result['circle']

        # 2. Join circle
        join_result = community_service.join_community_circle(self.validator1, circle.id)
        self.assertTrue(join_result['success'])

        # 3. Verify member count
        self.assertEqual(circle.member_count, 2)  # leader + 1 member

        # 4. Leave circle
        leave_result = community_service.leave_community_circle(self.validator1, circle.id)
        self.assertTrue(leave_result['success'])
        self.assertEqual(circle.member_count, 1)  # just leader


# Test utilities
class TestUtilities:
    """
    Utility functions for testing.
    """

    @staticmethod
    def create_test_bottle(bottle_id='TEST001', registered=False, user=None):
        """Create a test bottle"""
        bottle = Bottle.objects.create(
            bottle_id=bottle_id,
            batch_id='BATCH001',
            production_date='2023-01-01',
            terroir_region='Chablis',
            terroir_vintage='2022'
        )

        if registered and user:
            bottle.registered = True
            bottle.registered_to = user
            bottle.registration_date = timezone.now()
            bottle.status = 'registered'
            bottle.save()

        return bottle

    @staticmethod
    def create_test_pledge(user, bottle, status='pending'):
        """Create a test pledge"""
        return KarmaPledge.objects.create(
            user=user,
            bottle=bottle,
            pledge_text=f'Test pledge by {user.username}',
            impact_plan='Test impact plan implementation',
            impact_type='environmental',
            status=status
        )


# Run tests from command line
if __name__ == '__main__':
    import django

    django.setup()

    # Run specific test cases
    import unittest

    unittest.main()
