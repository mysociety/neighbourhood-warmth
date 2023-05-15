from django.contrib.auth.models import AbstractUser
from django.contrib.gis import measure
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point


class User(AbstractUser):
    pass


class Team(models.Model):
    name = models.CharField(max_length=100)
    base_pc = models.CharField(max_length=10)
    centroid = models.PointField()

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
