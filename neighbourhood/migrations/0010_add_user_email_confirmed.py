# Generated by Django 4.1 on 2023-05-22 13:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("neighbourhood", "0009_update_user_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_confirmed",
            field=models.BooleanField(default=False),
        ),
    ]
