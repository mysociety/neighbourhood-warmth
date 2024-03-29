# Generated by Django 4.1 on 2023-05-22 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0007_add_team_members"),
    ]

    operations = [
        migrations.CreateModel(
            name="Token",
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
                ("token", models.CharField(max_length=300)),
                (
                    "domain",
                    models.CharField(
                        choices=[("user", "User"), ("new_team", "New Team")],
                        max_length=50,
                    ),
                ),
                ("user_id", models.IntegerField()),
                ("domain_id", models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
