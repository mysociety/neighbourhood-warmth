# Generated by Django 4.2.15 on 2024-08-14 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0019_challenges"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="challenge",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="neighbourhood.challenge",
            ),
        ),
    ]