from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from neighbourhood.models import Membership, Team
from neighbourhood.utils import get_postcode_centroid

User = get_user_model()


teams_data = [
    {
        "name": "Warmer Whitewell",
        "address": "1 Delmore Rd, Frome, Somerset, BA11 4EG",
        "status": "recruiting for October retrofit assessments",
        "members": [
            "Saige Indie",
            "Kayson Berny",
            "Lauren Dillan",
            "Jacinda Bridger",
            "Roger Linton",
        ],
    },
    {
        "name": "Stonebridge Savers",
        "address": "71 Stonebridge Drive, Frome, Somerset, BA11 2TP",
        "status": "researching retrofit assessment providers",
        "members": [
            "Holly Thornton",
            "Carl Flint",
        ],
    },
    {
        "name": "Jamie’s Park Run Powerhouse",
        "address": "1 Woodland Road, Frome, BA11 1LE",
        "status": "looking for members",
        "members": [
            "Jamie McAlister",
        ],
    },
    {
        "name": "Retrofit Balsall Heath",
        "address": "81 Oakfield Road, Balsall Heath, Birmingham, B12 9PY",
        "status": "recruiting for October retrofit assessments",
        "members": [
            "Daniella Kitto",
            "Jay Lina",
            "Rajesh Chandra",
            "James Smith",
            "Toby Pierce",
        ],
    },
    {
        "name": "St Anne’s Community Group",
        "address": "St Anne’s church, Park Hill, Birmingham, B13 8DX",
        "status": "looking for members",
        "members": [
            "Ricky Brown",
            "Aparajita Neelam",
        ],
    },
    {
        "name": "Cosy Moseley",
        "address": "5 Ascot Road, Moseley, Birmingham, B13 9EN",
        "status": "researching retrofit assessment providers",
        "members": [
            "Ben Newton",
            "Krish Chatterjee",
            "Maddie Gilroy",
            "Dunstan Rose",
        ],
    },
    {
        "name": "Cosy Marchmont",
        "address": "31 Arden Street, Edinburgh, EH9 1BS",
        "status": "recruiting for October retrofit assessments",
        "members": [
            "Jim Luther",
            "Holly Mackenna",
            "Caelan Blythe",
            "Lou Douglas",
        ],
    },
    {
        "name": "New Town Power Station",
        "address": "2 Great King St, Edinburgh, EH3 6QH",
        "status": "researching retrofit assessment providers",
        "members": [
            "Neha Shivali",
            "Jessica Blair",
        ],
    },
    {
        "name": "Blackhall Coldbusters",
        "address": "11b House O'Hill Gardens, Edinburgh, EH4 2AR",
        "status": "looking for members",
        "members": [
            "Pooja Surya",
        ],
    },
]


def fake_email(name):
    return "{}@localhost".format(slugify(name))


def address_line(address, number):
    parts = address.split(",")
    if len(parts) <= number:
        return None
    else:
        return parts[number - 1].strip()


def postcode(address):
    return address.split(",")[-1].strip()


def lat_lon_from_postcode(pc):
    lat_lon = get_postcode_centroid(pc)
    if "error" in lat_lon:
        raise ValidationError(lat_lon["error"], code="invalid")
    else:
        return lat_lon


class Command(BaseCommand):
    help = "Load fake users and teams into the site"

    def add_arguments(self, parser):
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Do not print data as it is loaded",
        )

    def handle(self, quiet=False, *args, **options):
        self._quiet = quiet

        for team_data in teams_data:
            self.log("team {}", team_data["name"])

            base_pc = postcode(team_data["address"])
            lat_lon = lat_lon_from_postcode(base_pc)

            team_obj = {
                "name": team_data["name"],
                "address_1": address_line(team_data["address"], 1),
                "address_2": address_line(team_data["address"], 2),
                "address_3": address_line(team_data["address"], 3),
                "centroid": Point(lat_lon["lon"], lat_lon["lat"], srid=4326),
                "status": team_data["status"],
                "confirmed": True,
            }

            team, _ = Team.objects.update_or_create(base_pc=base_pc, defaults=team_obj)

            for index, member_name in enumerate(team_data["members"]):
                self.log("  user {}", member_name)

                user_obj = {
                    "full_name": member_name,
                    "email_confirmed": True,
                }

                user, _ = User.objects.update_or_create(
                    email=fake_email(member_name), defaults=user_obj
                )

                if index == 0:
                    team.creator = user
                    team.save()

                Membership.objects.update_or_create(
                    team=team,
                    user=user,
                    defaults={
                        "confirmed": True,
                        "is_admin": index < 2,
                    },
                )

    def log(self, message, *args):
        if not self._quiet:
            self.stdout.write(message.format(*args))
