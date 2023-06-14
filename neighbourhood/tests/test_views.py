import logging

from django.core import mail
from django.shortcuts import reverse
from django.test import TestCase
from neighbourhood.models import Membership, Team, User


class CorePageTest(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)


class TeamPagesTest(TestCase):
    fixtures = ["teams.json"]

    def test_existing_team(self):
        team = Team.objects.get(slug="holyrood-palace")

        response = self.client.get(reverse("team", args=("holyrood-palace",)))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(team.id, context["team"].id)

    def test_non_existing_team(self):
        response = self.client.get(reverse("team", args=("blenheim-palace",)))
        self.assertEqual(response.status_code, 404)

    def test_non_confirmed_team(self):
        response = self.client.get(reverse("team", args=("holyrood-palace-2",)))
        self.assertEqual(response.status_code, 404)


class TeamManagementPagesTest(TestCase):
    fixtures = ["teams.json", "memberships.json"]

    def test_team_management_page_access(self):
        # avoid printing out the PermissionDenied stack trace
        # XXX: almost certainly a better way to do this
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            reverse("confirm_join_team", args=("holyrood-palace",)),
        )
        self.assertEqual(response.status_code, 403)

        self.client.force_login(
            User.objects.get(email="new_holyrood_member@example.org")
        )
        response = self.client.get(
            reverse("confirm_join_team", args=("holyrood-palace",)),
        )
        self.assertEqual(response.status_code, 403)
        logging.disable(logging.NOTSET)

        self.client.force_login(User.objects.get(email="holyrood-admin@example.org"))
        response = self.client.get(
            reverse("confirm_join_team", args=("holyrood-palace",))
        )
        self.assertEqual(response.status_code, 200)
