import logging
import re
from unittest.mock import patch

from django.core import mail
from django.shortcuts import reverse
from django.test import TestCase, override_settings

from neighbourhood.models import Challenge, Team, User


class CorePageTest(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)


class CreateTeamTest(TestCase):
    @override_settings(CAN_CREATE_TEAMS=True)
    @patch("neighbourhood.utils.get_mapit_data")
    def test_create_team(self, mapit_get):
        mapit_get.return_value = {
            "postcode": "SP1 1SP",
            "wgs84_lon": -3.174588946918464,
            "wgs84_lat": 55.95206388207891,
            "coordsyst": "G",
            "easting": 326751,
            "northing": 673849,
            "areas": {
                "162673": {
                    "id": 162673,
                    "name": "Canongate, Southside and Dumbiedykes",
                    "type": "OMF",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"ons": "S22000059"},
                },
                "163747": {
                    "id": 163747,
                    "name": "Edinburgh",
                    "type": "TTW",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S22000059"},
                },
                "134935": {
                    "id": 134935,
                    "name": "Edinburgh Central",
                    "type": "SPC",
                    "type_name": "Scottish Parliament constituency",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S16000104", "unit_id": "41364"},
                },
                "14419": {
                    "id": 14419,
                    "name": "Edinburgh East",
                    "type": "WMC",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S14000022", "unit_id": "33667"},
                },
            },
        }

        url = reverse("create_team")

        with self.settings(CAN_CREATE_TEAMS=False):
            response = self.client.get(f"{url}?pc=SP1 1SP")
            self.assertRedirects(response, "/")

        response = self.client.get(f"{url}?pc=SP1 1SP")

        response = self.client.post(
            url,
            {
                "creator_name": "Team Creator",
                "email": "team_creator@example.org",
                "address_1": "",
                "address_2": "",
                "address_3": "",
                "base_pc": "SP1 1SP",
                "name": "Test Team",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/confirmation_sent/")

        self.assertEqual(len(mail.outbox), 1)

        t = Team.objects.get(name="Test Team")
        self.assertFalse(t.confirmed)

        areas = t.areas
        self.assertEqual(areas.count(), 4)
        codes = [a.code for a in areas.order_by("code")]
        self.assertEqual(
            codes,
            [
                "S",
                "S14000022",
                "S16000104",
                "S22000059",
            ],
        )

        sent = mail.outbox[0]
        self.assertEqual(
            sent.subject, "Neighbourhood Warmth: Verify your email address"
        )

        g = re.search(r"/activate/([^/]*)/", sent.body, re.MULTILINE)
        url = reverse("confirm_email", args=(g.group(1),))
        response = self.client.get(url)

        team_url = reverse("team", args=(t.slug,))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, team_url)


class TeamSearchTest(TestCase):
    fixtures = ["teams.json"]

    @patch("neighbourhood.utils.get_mapit_data")
    def test_search_for_area(self, mapit_get):
        mapit_get.return_value = {
            "postcode": "SP1 1SP",
            "lon": -3.174588946918464,
            "lat": 55.95206388207891,
        }

        url = reverse("search_results")
        response = self.client.get(url, {"pc": "SP1 1SP"})
        self.assertEqual(200, response.status_code)

        self.assertFalse(response.context["can_create_teams"])
        self.assertEquals(len(response.context["teams"]), 3)

        team_names = [t.name for t in response.context["teams"]]
        self.assertFalse("southwark 1" in team_names)

        with self.settings(CAN_CREATE_TEAMS=True):
            response = self.client.get(url, {"pc": "SP1 1SP"})
            self.assertTrue(response.context["can_create_teams"])


class TeamPagesTest(TestCase):
    fixtures = ["teams.json", "memberships.json"]

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

    def test_team_with_challenge_set(self):
        self.client.force_login(User.objects.get(email="holyrood-admin@example.org"))
        response = self.client.get(reverse("team", args=("holyrood-palace",)))

        self.assertContains(response, "Recruit your first team member")
        self.assertContains(response, "Recruit second team member")
        self.assertNotContains(response, "Find second member")

    def test_team_with_rich_challenge_set(self):
        challenge = Challenge.objects.get(name="Recruit second team member")
        team = Team.objects.get(slug="holyrood-palace")
        team.challenge = challenge
        team.save()

        self.client.force_login(User.objects.get(email="holyrood-admin@example.org"))
        response = self.client.get(reverse("team", args=("holyrood-palace",)))

        self.assertContains(response, "<p>Recruit your <b>second</b> team member")

    def test_team_with_non_default_template_challenge_set(self):
        challenge = Challenge.objects.get(name="Recruit first team member")
        challenge.template = "neighbourhood/challenges/_recruit_members.html"
        challenge.save()

        self.client.force_login(User.objects.get(email="holyrood-admin@example.org"))
        response = self.client.get(reverse("team", args=("holyrood-palace",)))

        self.assertContains(response, "Use the share buttons below")

    def test_team_with_bad_template_challenge_set(self):
        challenge = Challenge.objects.get(name="Recruit first team member")
        challenge.template = "neighbourhood/challenges/_missing.html"
        challenge.save()

        self.client.force_login(User.objects.get(email="holyrood-admin@example.org"))
        response = self.client.get(reverse("team", args=("holyrood-palace",)))

        self.assertContains(response, "Recruit your first team member")

    def test_team_with_no_challenge_set(self):
        self.client.force_login(
            User.objects.get(email="scottishparliament-admin@example.org")
        )

        response = self.client.get(reverse("team", args=("scottish-parliament",)))

        self.assertNotContains(response, "Recruit second team member")
        self.assertContains(response, "Find second member")


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


class AreaSearchTest(TestCase):
    @patch("neighbourhood.utils.get_mapit_data")
    def test_search_for_area(self, mapit_get):
        mapit_get.return_value = {
            "postcode": "SP1 1SP",
            "wgs84_lon": -3.174588946918464,
            "wgs84_lat": 55.95206388207891,
            "coordsyst": "G",
            "easting": 326751,
            "northing": 673849,
            "areas": {
                "163747": {
                    "id": 163747,
                    "name": "Edinburgh",
                    "type": "TTW",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S22000059"},
                },
                "134935": {
                    "id": 134935,
                    "name": "Edinburgh Central",
                    "type": "SPC",
                    "type_name": "Scottish Parliament constituency",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S16000104", "unit_id": "41364"},
                },
                "2651": {
                    "id": 2651,
                    "name": "City of Edinburgh Council",
                    "type": "UTA",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S12000036"},
                },
            },
        }

        url = reverse("area_search")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        expected_url = reverse("area", args=("S12000036",))
        response = self.client.post(url, {"pc": "SP1 1SP"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    @patch("neighbourhood.utils.get_mapit_data")
    def test_area_search_multi_match(self, mapit_get):
        mapit_get.return_value = {
            "postcode": "SP1 1SP",
            "wgs84_lon": -3.174588946918464,
            "wgs84_lat": 55.95206388207891,
            "coordsyst": "G",
            "easting": 326751,
            "northing": 673849,
            "areas": {
                "134935": {
                    "id": 134935,
                    "name": "Edinburgh Central",
                    "type": "DIS",
                    "type_name": "Fake Edinburgh Council",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S16000104", "unit_id": "41364"},
                },
                "2651": {
                    "id": 2651,
                    "name": "City of Edinburgh Council",
                    "type": "UTA",
                    "country": "S",
                    "country_name": "Scotland",
                    "codes": {"gss": "S12000036"},
                },
            },
        }

        url = reverse("area_search")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        response = self.client.post(url, {"pc": "SP1 1SP"})

        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(2, len(context["matching_areas"]))
