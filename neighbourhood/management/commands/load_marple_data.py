import json
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize
from django.utils.text import slugify

from neighbourhood.models import Membership, Team
from neighbourhood.services.teams import add_areas_to_team
from neighbourhood.utils import get_postcode_data

User = get_user_model()


def fake_email(name):
    return "{}@localhost".format(slugify(name))


class Command(BaseCommand):
    help = "Load a Marple user and team into the site"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            help="Delete all teams and all non-staff users before loading fake data",
        )

        parser.add_argument(
            "-D",
            "--delete-only",
            action="store_true",
            help="Delete all teams and all non-staff users, and then stop, without loading any new data",
        )

    def handle(self, verbosity, delete=False, delete_only=False, *args, **options):
        self.verbosity = verbosity

        if delete or delete_only:
            teams = Team.objects.all()
            users = User.objects.filter(is_staff=False)
            self.log(
                "deleting {} {} and {} non-staff {}".format(
                    teams.count(),
                    pluralize(teams.count(), "team,teams"),
                    users.count(),
                    pluralize(users.count(), "user,users"),
                )
            )

            teams.delete()
            users.delete()

            if delete_only:
                exit()

        geojson_file_path = os.path.join(
            settings.BASE_DIR, "neighbourhood", "fixtures", "marple.geojson"
        )
        with open(geojson_file_path, "r") as file:
            try:
                geojson_data = json.load(file)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f"Error decoding JSON: {e}"))
                return

        base_pc = geojson_data["properties"]["centroid_postcode"]
        postcode_data = get_postcode_data(base_pc)

        team_obj = {
            "name": "Powershaper Flex Marple",
            "address_1": "",
            "address_2": "Marple",
            "address_3": "Greater Manchester",
            "centroid": Point(
                geojson_data["properties"]["centroid_x"],
                geojson_data["properties"]["centroid_y"],
                srid=4326,
            ),
            "boundary": GEOSGeometry(json.dumps(geojson_data["geometry"])),
            "status": "recruiting for a Spring 2025 flexibility tender",
            "confirmed": True,
        }

        self.log("creating team {}".format(team_obj["name"]))
        team, _ = Team.objects.update_or_create(base_pc=base_pc, defaults=team_obj)

        add_areas_to_team(team, postcode_data["areas"])

        user_obj = {
            "full_name": "Miss Marple",
            "email_confirmed": True,
        }

        self.log("creating user {}".format(user_obj["full_name"]))
        user, _ = User.objects.update_or_create(
            email=fake_email(user_obj["full_name"]), defaults=user_obj
        )

        team.creator = user
        team.save()

        Membership.objects.update_or_create(
            team=team,
            user=user,
            defaults={
                "confirmed": True,
                "is_admin": True,
            },
        )

    def log(self, message, *args):
        if self.verbosity != 0:
            self.stdout.write(message.format(*args))
