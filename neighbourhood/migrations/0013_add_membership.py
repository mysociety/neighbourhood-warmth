# Generated by Django 4.1 on 2023-05-23 16:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0012_remove_team_membership"),
    ]

    operations = [
        migrations.CreateModel(
            name="Membership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("confirmed", models.BooleanField(default=False)),
                ("date_joined", models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name="team",
            name="members",
            field=models.ManyToManyField(
                related_name="teams",
                related_query_name="team",
                through="neighbourhood.Membership",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="neighbourhood.team"
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]