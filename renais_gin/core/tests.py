from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Bottle, KarmaPledge, MovementMetrics


User = get_user_model()


class PledgeReviewIntegrityTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="pledge-author",
            password="test-only-password",
        )
        self.reviewers = [
            User.objects.create_user(
                username=f"reviewer-{index}",
                password="test-only-password",
            )
            for index in range(1, 5)
        ]
        self.bottle = Bottle.objects.create(
            bottle_id="TEST-BOTTLE-001",
            batch_id="TEST-BATCH",
            production_date=date(2026, 1, 1),
            terroir_data={"region": "test"},
            registered=True,
            registered_to=self.author,
        )

    def test_heuristic_submission_always_waits_for_community_review(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("core:submit_pledge", args=[self.bottle.bottle_id]),
            {
                "pledge_text": (
                    "I will plant trees, help the community, support a sustainable "
                    "garden, improve our neighborhood, create green space and support "
                    "local education through a community planting project."
                ),
                "impact_plan": "Organize a community planting day and help maintain it.",
            },
        )

        self.assertEqual(response.status_code, 302)
        pledge = KarmaPledge.objects.get(user=self.author, bottle=self.bottle)
        self.assertEqual(pledge.status, "needs_review")
        self.assertEqual(pledge.approvals, 0)
        self.assertFalse(pledge.rebate_processed)

    def test_each_account_can_validate_a_pledge_only_once(self):
        pledge = KarmaPledge.objects.create(
            submission_id="TEST-PLEDGE-DUPLICATE",
            user=self.author,
            bottle=self.bottle,
            pledge_text="A test pledge",
            impact_plan="A test plan",
            status="needs_review",
        )
        self.client.force_login(self.reviewers[0])
        url = reverse("core:validate_pledge", args=[pledge.pk])

        first = self.client.post(url, {"approval": "true", "comments": "Looks good"})
        second = self.client.post(url, {"approval": "true", "comments": "Second vote"})

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        pledge.refresh_from_db()
        self.assertEqual(pledge.approvals, 1)
        self.assertEqual(len(pledge.validations), 1)
        self.assertFalse(pledge.rebate_processed)

    def test_community_approval_does_not_claim_that_a_rebate_was_paid(self):
        pledge = KarmaPledge.objects.create(
            submission_id="TEST-PLEDGE-APPROVAL",
            user=self.author,
            bottle=self.bottle,
            pledge_text="A test pledge",
            impact_plan="A test plan",
            status="needs_review",
        )
        url = reverse("core:validate_pledge", args=[pledge.pk])

        for reviewer in self.reviewers[:3]:
            self.client.force_login(reviewer)
            response = self.client.post(url, {"approval": "true", "comments": "Approved"})
            self.assertEqual(response.status_code, 302)

        pledge.refresh_from_db()
        self.assertEqual(pledge.approvals, 3)
        self.assertEqual(pledge.status, "approved")
        self.assertFalse(pledge.rebate_processed)
        self.assertEqual(len(pledge.validations), 3)

    def test_public_metrics_get_does_not_refresh_or_create_metrics(self):
        response = self.client.get(reverse("core:api_metrics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_pledges"], 0)
        self.assertEqual(response.json()["last_updated"], None)
        self.assertEqual(MovementMetrics.objects.count(), 0)

    def test_public_metrics_endpoint_rejects_post(self):
        response = self.client.post(reverse("core:api_metrics"), {"refresh": True})

        self.assertEqual(response.status_code, 405)
        self.assertEqual(MovementMetrics.objects.count(), 0)
