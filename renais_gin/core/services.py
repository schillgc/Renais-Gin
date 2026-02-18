"""
Business logic services for Renais Gin core functionality.
"""

import hashlib
import json
from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError

# Use get_user_model() instead of direct User import
User = get_user_model()

from .models import (
    Bottle, KarmaPledge, PledgeValidation, Rebate,
    CommunityCircle, UserProfile
)
from .ai_services import RenaissanceAICore


class RenaisGinService:
    """
    Main service class for Renais Gin business logic.
    """

    def __init__(self):
        self.ai_core = RenaissanceAICore()

    @transaction.atomic
    def register_bottle(self, bottle_data: dict, user: User) -> dict:
        """
        Register a new bottle to a user.

        Args:
            bottle_data: Dictionary containing bottle information
            user: The user registering the bottle

        Returns:
            Dictionary with success status and data/error message
        """
        try:
            # Check if bottle already exists and is unregistered
            try:
                bottle = Bottle.objects.get(bottle_id=bottle_data['bottle_id'])
                if bottle.registered:
                    return {
                        'success': False,
                        'error': 'Bottle ID already registered'
                    }
            except Bottle.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Bottle ID not found in system'
                }

            # Update bottle registration
            bottle.registered = True
            bottle.registered_to = user
            bottle.registration_date = datetime.now()
            bottle.status = 'registered'
            bottle.save()

            # Update user engagement score
            self._update_user_engagement(user)

            return {
                'success': True,
                'bottle': bottle,
                'qr_code': bottle.qr_code.url if bottle.qr_code else None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @transaction.atomic
    def submit_pledge(self, user: User, bottle_id: str,
                      pledge_text: str, impact_plan: str) -> dict:
        """
        Submit a new karma pledge.

        Args:
            user: The user making the pledge
            bottle_id: ID of the bottle being pledged for
            pledge_text: The pledge statement
            impact_plan: Detailed impact implementation plan

        Returns:
            Dictionary with success status and data/error message
        """
        try:
            bottle = Bottle.objects.get(bottle_id=bottle_id, registered_to=user)

            # Validate bottle eligibility
            if not bottle.can_make_pledge():
                return {
                    'success': False,
                    'error': 'Bottle is not eligible for pledging'
                }

            # AI validation
            ai_result = self.ai_core.process_pledge_submission(
                user.id, bottle_id, pledge_text, impact_plan
            )

            # Generate submission ID
            submission_id = hashlib.sha256(
                f"{user.id}{bottle_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]

            # Determine initial status based on AI validation
            if ai_result['status'] == 'approved':
                initial_status = 'pending'  # Needs community validation
            elif ai_result['status'] == 'needs_review':
                initial_status = 'needs_review'
            else:
                initial_status = 'rejected'

            # Create pledge
            pledge = KarmaPledge.objects.create(
                user=user,
                bottle=bottle,
                pledge_text=pledge_text,
                impact_plan=impact_plan,
                impact_type=self.ai_core.classify_impact_type(impact_plan),
                sentiment_score=ai_result.get('score'),
                status=initial_status,
                submission_id=submission_id,
                ai_validation_data=ai_result
            )

            # Update bottle status
            bottle.status = 'pledged'
            bottle.save()

            # Create rebate record if AI approved
            if ai_result['status'] == 'approved':
                Rebate.objects.create(pledge=pledge)

            # Update user engagement score
            self._update_user_engagement(user)

            return {
                'success': True,
                'pledge': pledge,
                'ai_validation': ai_result
            }

        except Bottle.DoesNotExist:
            return {
                'success': False,
                'error': 'Bottle not found or not registered to user'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @transaction.atomic
    def validate_pledge(self, validator: User, pledge_id: str,
                        approval: bool, comments: str = '',
                        ip_address: str = None, user_agent: str = None) -> dict:
        """
        Validate a pledge as a community member.

        Args:
            validator: User performing the validation
            pledge_id: ID of the pledge to validate
            approval: Whether the pledge is approved
            comments: Optional comments about the validation
            ip_address: Validator's IP address
            user_agent: Validator's user agent string

        Returns:
            Dictionary with success status
        """
        try:
            pledge = KarmaPledge.objects.get(id=pledge_id)

            # Cannot validate your own pledge
            if pledge.user == validator:
                return {
                    'success': False,
                    'error': 'Cannot validate your own pledge'
                }

            # Check if already validated
            if PledgeValidation.objects.filter(
                    pledge=pledge, validator=validator
            ).exists():
                return {
                    'success': False,
                    'error': 'You have already validated this pledge'
                }

            # Create validation record
            validation = PledgeValidation.objects.create(
                pledge=pledge,
                validator=validator,
                approved=approval,
                comments=comments,
                validator_ip=ip_address,
                validator_user_agent=user_agent
            )

            # Update pledge status if enough validations
            self._update_pledge_status(pledge)

            # Update validator's engagement score
            self._update_user_engagement(validator)

            return {
                'success': True,
                'validation': validation
            }

        except KarmaPledge.DoesNotExist:
            return {
                'success': False,
                'error': 'Pledge not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_metrics(self, user: User) -> dict:
        """
        Get comprehensive user engagement and impact metrics.

        Args:
            user: User to get metrics for

        Returns:
            Dictionary with user metrics
        """
        try:
            profile = UserProfile.objects.get(user=user)
            pledges = KarmaPledge.objects.filter(user=user)
            bottles = Bottle.objects.filter(registered_to=user)
            validations_given = PledgeValidation.objects.filter(validator=user)

            # Calculate various metrics
            approved_pledges = pledges.filter(status='approved')
            total_impact = approved_pledges.count() * settings.RENAIS_SETTINGS['REBATE_AMOUNT']

            return {
                'total_pledges': pledges.count(),
                'approved_pledges': approved_pledges.count(),
                'pending_pledges': pledges.filter(status='pending').count(),
                'total_bottles': bottles.count(),
                'validations_given': validations_given.count(),
                'engagement_score': profile.engagement_score,
                'karma_score': profile.karma_score,
                'total_impact': float(total_impact),
                'preferred_causes': profile.preferred_causes,
                'member_since': user.date_joined.strftime('%B %Y'),
            }
        except Exception as e:
            return {'error': str(e)}

    def get_movement_metrics(self) -> dict:
        """
        Get global movement metrics.

        Returns:
            Dictionary with global movement metrics
        """
        from django.db.models import Count, Q

        total_bottles = Bottle.objects.count()
        total_pledges = KarmaPledge.objects.count()
        approved_pledges = KarmaPledge.objects.filter(status='approved').count()

        # FIX: Use get_user_model() instead of direct User import
        User = get_user_model()
        total_community = User.objects.filter(is_active=True).count()

        total_rebates = Rebate.objects.filter(status='completed').count()

        # Impact by category
        impact_by_category = KarmaPledge.objects.filter(
            status='approved'
        ).values('impact_type').annotate(count=Count('id'))

        # Community circles stats
        active_circles = CommunityCircle.objects.filter(is_active=True).count()
        total_circle_members = CommunityCircle.objects.aggregate(
            total_members=Count('members')
        )['total_members'] or 0
        total_circle_members += active_circles  # Add leaders

        return {
            'total_community': total_community,
            'total_bottles': total_bottles,
            'total_pledges': total_pledges,
            'approved_pledges': approved_pledges,
            'total_rebates': total_rebates,
            'total_impact': approved_pledges * settings.RENAIS_SETTINGS['REBATE_AMOUNT'],
            'active_circles': active_circles,
            'total_circle_members': total_circle_members,
            'impact_by_category': {item['impact_type']: item['count'] for item in impact_by_category},
        }

    # Private helper methods
    def _update_pledge_status(self, pledge: KarmaPledge):
        """Update pledge status based on validation count."""
        validations = pledge.validations.all()
        approval_count = validations.filter(approved=True).count()
        rejection_count = validations.filter(approved=False).count()

        required_approvals = settings.RENAIS_SETTINGS['COMMUNITY_VALIDATIONS_REQUIRED']

        if approval_count >= required_approvals:
            pledge.status = 'approved'
            pledge.save()

            # Ensure rebate exists
            if not hasattr(pledge, 'rebate'):
                Rebate.objects.create(pledge=pledge)

        elif rejection_count >= required_approvals:
            pledge.status = 'rejected'
            pledge.save()

    def _update_user_engagement(self, user: User):
        """Update user engagement score."""
        try:
            profile = UserProfile.objects.get(user=user)
            profile.update_engagement_score()
        except UserProfile.DoesNotExist:
            pass

    def process_rebate_payment(self, rebate_id: str) -> dict:
        """
        Process a rebate payment.

        Args:
            rebate_id: ID of the rebate to process

        Returns:
            Dictionary with processing result
        """
        try:
            rebate = Rebate.objects.get(id=rebate_id)

            if rebate.status != 'pending':
                return {
                    'success': False,
                    'error': f'Rebate already {rebate.status}'
                }

            # Mark as processing
            rebate.mark_processing()

            # Simulate payment processing
            # In production, integrate with actual payment processor
            transaction_id = f"TXN_{rebate.id.hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Mark as completed
            rebate.mark_completed(transaction_id)

            return {
                'success': True,
                'rebate': rebate,
                'transaction_id': transaction_id
            }

        except Rebate.DoesNotExist:
            return {
                'success': False,
                'error': 'Rebate not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class CommunityService:
    """
    Service class for community-related operations.
    """

    @transaction.atomic
    def create_community_circle(self, name: str, location: str,
                                leader: User, description: str = '',
                                focus_areas: list = None) -> dict:
        """
        Create a new community circle.

        Args:
            name: Circle name
            location: Circle location
            leader: Circle leader
            description: Circle description
            focus_areas: List of focus areas

        Returns:
            Dictionary with creation result
        """
        try:
            # Check if user already leads a circle
            if CommunityCircle.objects.filter(leader=leader, is_active=True).exists():
                return {
                    'success': False,
                    'error': 'You already lead an active community circle'
                }

            circle = CommunityCircle.objects.create(
                name=name,
                location=location,
                leader=leader,
                description=description,
                focus_areas=focus_areas or []
            )

            # Update leader's engagement score
            RenaisGinService()._update_user_engagement(leader)

            return {
                'success': True,
                'circle': circle
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def join_community_circle(self, user: User, circle_id: str) -> dict:
        """
        Add a user to a community circle.

        Args:
            user: User to add
            circle_id: Circle ID to join

        Returns:
            Dictionary with join result
        """
        try:
            circle = CommunityCircle.objects.get(id=circle_id, is_active=True)

            if circle.leader == user:
                return {
                    'success': False,
                    'error': 'You are already the leader of this circle'
                }

            if circle.members.filter(id=user.id).exists():
                return {
                    'success': False,
                    'error': 'You are already a member of this circle'
                }

            circle.add_member(user)

            # Update user's engagement score
            RenaisGinService()._update_user_engagement(user)

            return {
                'success': True,
                'circle': circle
            }

        except CommunityCircle.DoesNotExist:
            return {
                'success': False,
                'error': 'Community circle not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def leave_community_circle(self, user: User, circle_id: str) -> dict:
        """
        Remove a user from a community circle.

        Args:
            user: User to remove
            circle_id: Circle ID to leave

        Returns:
            Dictionary with leave result
        """
        try:
            circle = CommunityCircle.objects.get(id=circle_id, is_active=True)

            if circle.leader == user:
                return {
                    'success': False,
                    'error': 'Leaders cannot leave their circle. Transfer leadership first.'
                }

            if not circle.members.filter(id=user.id).exists():
                return {
                    'success': False,
                    'error': 'You are not a member of this circle'
                }

            circle.remove_member(user)

            return {
                'success': True,
                'circle': circle
            }

        except CommunityCircle.DoesNotExist:
            return {
                'success': False,
                'error': 'Community circle not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
