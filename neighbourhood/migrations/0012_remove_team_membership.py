# Generated by Django 4.1 on 2023-05-23 16:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0011_add_team_confirmed"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="team",
            name="members",
        ),
    ]
