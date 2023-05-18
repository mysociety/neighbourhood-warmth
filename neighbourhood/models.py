from random import randrange

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.gis import measure
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    full_name = models.CharField(max_length=200, blank=True, null=True)

    objects = MyUserManager()


class Team(models.Model):
    name = models.CharField(max_length=100)
    base_pc = models.CharField(max_length=10)
    centroid = models.PointField()
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

    status = models.CharField(max_length=300, blank=True, null=True)

    members = models.ManyToManyField(
        User, related_name="teams", related_query_name="team"
    )

    def members_count(self):
        return self.members.count()

    @classmethod
    def find_nearest_teams(self, latitude=None, longitude=None, distance=5):
        if latitude is None or longitude is None:
            return []

        max_distance = measure.Distance(km=distance)
        location = Point(longitude, latitude, srid=4326)
        nearest = (
            self.objects.annotate(distance=Distance("centroid", location))
            .filter(distance__lte=max_distance.m)
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


@receiver(pre_save, sender=Team)
def generate_team_slug(sender, instance, raw, using, update_fields, **kwargs):
    slug = instance.slug
    if slug is None or slug == "":
        slug = slugify(instance.name)
        postfix = randrange(100000)
        slug = f"{slug}-{postfix}"
        instance.slug = slug
