# Generated by Django 4.1 on 2024-10-04 13:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0024_team_boundary"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Detailed text content (plain text or HTML) shown on the public team page",
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="has_rich_description",
            field=models.BooleanField(
                default=False, help_text="True if description is raw HTML"
            ),
        ),
    ]
