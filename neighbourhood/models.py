from random import randrange

from django import template
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.gis import measure
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core.mail import mail_admins
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    email_confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    full_name = models.CharField(max_length=200, blank=True, null=True)

    objects = MyUserManager()


class Area(models.Model):
    AREA_TYPES = {
        "CTY": "county council",
        "CED": "county ward",
        "DIS": "district council",
        "DIW": "district ward",
        "LAC": "London Assembly constituency",
        "LBO": "London borough",
        "LBW": "London ward",
        "LGD": "NI council",
        "LGE": "NI electoral area",
        "LGW": "NI ward",
        "MTD": "Metropolitan district",
        "MTW": "Metropolitan ward",
        "NIE": "NI Assembly constituency",
        "OLF": "Lower Layer Super Output Area, Full",
        "OLG": "Lower Layer Super Output Area, Generalised",
        "OMF": "Middle Layer Super Output Area, Full",
        "OMG": "Middle Layer Super Output Area, Generalised",
        "SPC": "Scottish Parliament constituency",
        "SPE": "Scottish Parliament region",
        "UTA": "Unitary authority",
        "UTE": "Unitary authority electoral division",
        "UTW": "Unitary authority ward",
        "WAC": "Welsh Assembly constituency",
        "WAE": "Welsh Assembly region",
        "WMC": "UK Parliamentary constituency",
    }

    COUNCIL_TYPES = [
        "CTY",
        "DIS",
        "LBO",
        "LGD",
        "MTD",
        "UTA",
    ]

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=300)
    area_type = models.CharField(max_length=20)
    # need this to look up geometry
    mapit_id = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["area_type"]),
        ]

    def __str__(self):
        return "{} ({} {})".format(self.name, self.area_type, self.mapit_id)


class Challenge(models.Model):
    name = models.CharField(max_length=300)
    short_description = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="A one line summary of the challenge, suitable for public view",
    )
    description = models.TextField(
        help_text="Detailed text content (plain text or HTML) shown to signed-in team members"
    )
    template = models.CharField(
        max_length=300, help_text=f"Default: {settings.DEFAULT_CHALLENGE_TEMPLATE}"
    )
    is_active = models.BooleanField(
        default=True, help_text="Inactive challenges are not displayed anywhere"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Private challenges are shown only to signed-in team members",
    )
    order = models.IntegerField()

    has_rich_description = models.BooleanField(
        default=False, help_text="True if description is raw HTML"
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_template_safe(self):
        try:
            template.loader.get_template(self.template)
            return self.template
        except template.TemplateDoesNotExist:
            mail_admins(
                "Bad challenge template",
                f"Challenge {self.name} template not found: {self.template}",
            )
            return settings.DEFAULT_CHALLENGE_TEMPLATE

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    base_pc = models.CharField(max_length=10)
    centroid = models.PointField()
    boundary = models.PolygonField(blank=True, null=True)
    slug = models.CharField(
        max_length=100, blank=True, null=True, default="", unique=True
    )

    address_1 = models.CharField(max_length=300, blank=True, null=True)
    address_2 = models.CharField(max_length=300, blank=True, null=True)
    address_3 = models.CharField(max_length=300, blank=True, null=True)

    # we don't want the team to vanish if we remove the creator so allow it to be
    # set to null
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL, blank=True, null=True
    )

    confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=300, blank=True, null=True)

    challenge = models.ForeignKey(
        Challenge, on_delete=models.SET_NULL, blank=True, null=True
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # BEWARE! This includes unconfirmed applicants and rejected members!
    members = models.ManyToManyField(
        User, related_name="teams", related_query_name="team", through="Membership"
    )

    areas = models.ManyToManyField(
        Area, related_name="teams", related_query_name="teams"
    )

    def __str__(self):
        return self.name

    @property
    def confirmed_members(self):
        return self.members.filter(membership__confirmed=True)

    def vicinity(self):
        return self.address_3 if self.address_3 else self.address_2

    @property
    def admins(self):
        return User.objects.filter(team=self, membership__is_admin=True)

    def available_challenges(self, public_only=False):
        # if there's no challenge set then use the default ones
        if self.challenge is None:
            return []

        challenges = Challenge.objects.filter(is_active=True).order_by("order")
        if public_only:
            challenges = challenges.filter(is_public=True)

        current_place = 0
        if self.challenge:
            current_place = self.challenge.order

        challenge_details = []
        for challenge in challenges:
            details = {
                "challenge": challenge,
            }

            if challenge.order < current_place:
                details["done"] = True
            elif challenge.order == current_place:
                details["active"] = True

            challenge_details.append(details)

        return challenge_details

    @classmethod
    def find_nearest_teams(self, latitude=None, longitude=None, distance=5):
        if latitude is None or longitude is None:
            return []

        max_distance = measure.Distance(km=distance)
        location = Point(longitude, latitude, srid=4326)
        nearest = (
            self.objects.annotate(distance=Distance("centroid", location))
            .filter(distance__lte=max_distance.m, confirmed=True)
            .order_by("distance")
        )

        return nearest

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "slug",
                ]
            )
        ]


class Membership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Token(models.Model):
    DOMAINS = [("user", "User"), ("new_team", "New Team"), ("login", "Login")]
    token = models.CharField(max_length=300)
    domain = models.CharField(max_length=50, choices=DOMAINS)
    user_id = models.IntegerField()
    domain_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.token


@receiver(pre_save, sender=Team)
def generate_team_slug(sender, instance, raw, using, update_fields, **kwargs):
    slug = instance.slug
    if slug is None or slug == "":
        slug = slugify(instance.name)
        postfix = randrange(100000)
        slug = f"{slug}-{postfix}"
        instance.slug = slug
