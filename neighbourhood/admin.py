from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Team, User

admin.site.register(User, UserAdmin)


@admin.register(Team)
class TeamAdmin(OSMGeoAdmin):
    list_display = ("name", "centroid")
