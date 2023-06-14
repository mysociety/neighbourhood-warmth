from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory
from neighbourhood.models import Membership, Team, User
from neighbourhood.services.teams import (notify_membership_confirmed,
                                          notify_membership_rejected,
                                          notify_new_member)


class NotificationEmailTest(TestCase):
    fixtures = ["groups.json", "memberships.json"]

    def setUp(self):
        self.factory = RequestFactory()

    def test_new_member_email(self):
        r = self.factory.get("/teams/holyrood-palace/")
        t = Team.objects.get(slug="holyrood-palace")
        u = User.objects.get(email="new_holyrood_member@example.org")
        s = get_current_site(r)

        notify_new_member(t, u, s)

        self.assertEqual(len(mail.outbox), 1)

        admin = User.objects.get(email="holyrood-admin@example.org")
        admin2 = User.objects.get(email="holyrood-admin-2@example.org")

        sent = mail.outbox[0]
        self.assertEqual(sent.subject, "New member for team Holyrood palace")
        self.assertEqual(sent.to, [])
        self.assertEqual(sent.bcc, [admin.email, admin2.email])

    def test_membership_rejected_email(self):
        r = self.factory.get("/teams/holyrood-palace/")
        t = Team.objects.get(slug="holyrood-palace")
        u = User.objects.get(email="new_holyrood_member@example.org")
        m = Membership.objects.get(user=u, team=t)
        s = get_current_site(r)

        notify_membership_rejected(t, u, m, s)

        self.assertEqual(len(mail.outbox), 1)

        sent = mail.outbox[0]
        self.assertEqual(
            sent.subject, "Your request to join a Neighbourhood Warmth Team"
        )
        self.assertRegex(sent.body, r"Thanks for applying to join Holyrood palace")
        self.assertRegex(sent.body, r"hasn’t accepted")

    def test_membership_confirmed_email(self):
        r = self.factory.get("/teams/holyrood-palace/")
        t = Team.objects.get(slug="holyrood-palace")
        u = User.objects.get(email="new_holyrood_member@example.org")
        m = Membership.objects.get(user=u, team=t)
        s = get_current_site(r)

        notify_membership_confirmed(t, u, m, s)

        self.assertEqual(len(mail.outbox), 1)

        sent = mail.outbox[0]
        self.assertEqual(
            sent.subject, "Your request to join a Neighbourhood Warmth Team"
        )
        self.assertRegex(
            sent.body, r"Holyrood palace has approved your request to join"
        )
        self.assertNotRegex(sent.body, r"given permission")

    def test_membership_confirmed_admin_email(self):
        r = self.factory.get("/teams/holyrood-palace/")
        t = Team.objects.get(slug="holyrood-palace")
        u = User.objects.get(email="new_holyrood_member@example.org")
        m = Membership.objects.get(user=u, team=t)
        m.is_admin = True
        m.save()
        s = get_current_site(r)

        notify_membership_confirmed(t, u, m, s)

        self.assertEqual(len(mail.outbox), 1)

        sent = mail.outbox[0]
        self.assertEqual(
            sent.subject, "Your request to join a Neighbourhood Warmth Team"
        )
        self.assertRegex(
            sent.body, r"Holyrood palace has approved your request to join"
        )
        self.assertRegex(sent.body, r"given permission")
