# Generated by Django 4.1 on 2023-05-24 15:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0013_add_membership"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]
