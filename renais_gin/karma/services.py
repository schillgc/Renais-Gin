# karma/services.py
import hashlib
from datetime import datetime
from django.db import transaction
from django.conf import settings
from .models import KarmaPledge, KarmaValidation, KarmaRebate
from blockchain.services import BlockchainService
from ai_agents.services import AIService


class KarmaEconomyService:
    def __init__(self):
        self.blockchain = BlockchainService()
        self.ai_service = AIService()

    def submit_pledge(self, user, bottle, pledge_text: str, impact_plan: str) -> KarmaPledge:
        """Submit a new karma pledge for validation"""
        with transaction.atomic():
            # Generate unique submission ID
            submission_id = hashlib.sha256(
                f"{user.id}{bottle.id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]

            # AI validation
            ai_result = self.ai_service.validate_pledge(pledge_text, impact_plan)

            # Create pledge
            pledge = KarmaPledge.objects.create(
                submission_id=submission_id,
                user=user,
                bottle=bottle,
                pledge_text=pledge_text,
                impact_plan=impact_plan,
                ai_confidence_score=ai_result.get('score'),
                status=ai_result.get('status', KarmaPledge.STATUS_PENDING)
            )

            # Record on blockchain
            self.blockchain.record_pledge_submission(
                submission_id=submission_id,
                user_id=str(user.id),
                bottle_id=bottle.bottle_id
            )

            return pledge

    def process_validation(self, validator, pledge_id: str, approval: bool, comments: str = "") -> bool:
        """Process a community validation"""
        with transaction.atomic():
            try:
                pledge = KarmaPledge.objects.get(id=pledge_id)

                # Check if already validated by this user
                if KarmaValidation.objects.filter(pledge=pledge, validator=validator).exists():
                    return False

                # Create validation record
                validation = KarmaValidation.objects.create(
                    pledge=pledge,
                    validator=validator,
                    approval=approval,
                    comments=comments
                )

                # Update pledge counts
                if approval:
                    pledge.approvals += 1
                else:
                    pledge.rejections += 1

                # Check if validation threshold is met
                if pledge.approvals >= settings.AI_AGENTS['COMMUNITY_APPROVALS_REQUIRED']:
                    pledge.status = KarmaPledge.STATUS_APPROVED
                    self._create_rebate(pledge)

                elif pledge.rejections >= 2:  # Rejection threshold
                    pledge.status = KarmaPledge.STATUS_REJECTED

                pledge.save()

                # Record on blockchain
                self.blockchain.record_validation(
                    submission_id=pledge.submission_id,
                    validator_id=str(validator.id),
                    approval=approval
                )

                return True

            except KarmaPledge.DoesNotExist:
                return False

    def _create_rebate(self, pledge: KarmaPledge):
        """Create rebate for approved pledge"""
        rebate = KarmaRebate.objects.create(
            pledge=pledge,
            user=pledge.user,
            amount=settings.KARMA_ECONOMY['REBATE_AMOUNT']
        )

        # Update user profile
        profile = pledge.user.profile
        profile.approved_pledges += 1
        profile.total_rebates += rebate.amount
        profile.save()

        return rebate
