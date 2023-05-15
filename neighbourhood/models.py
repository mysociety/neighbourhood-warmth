from django.contrib.auth.models import AbstractUser
from django.contrib.gis import measure
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


class User(AbstractUser):
    pass


class Team(models.Model):
    name = models.CharField(max_length=100)
    base_pc = models.CharField(max_length=10)
    centroid = models.PointField()
    slug = models.CharField(max_length=100, blank=True, null=True, default="")

    @classmethod
    def find_nearest_groups(self, latitude=None, longitude=None, distance=5):
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
    if slug is None:
        slug = slugify(instance.name)
        instance.slug = slug
