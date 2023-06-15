from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from neighbourhood.models import Area


def notify_new_member(team, member, site):
    admins = [a.email for a in team.admins]

    mail_subject = render_to_string(
        "neighbourhood/teams/new_member_subject.txt",
        {
            "team": team,
        },
    ).strip()
    message = render_to_string(
        "neighbourhood/teams/new_member_email.html",
        {
            "user": member,
            "team": team,
            "domain": site.domain,
        },
    )
    email = EmailMessage(mail_subject, message, bcc=admins)
    email.send()


def notify_member_change(team, member, membership, site, change):
    mail_subject = render_to_string(
        f"neighbourhood/teams/membership_{change}_subject.txt"
    ).strip()
    message = render_to_string(
        f"neighbourhood/teams/membership_{change}_email.html",
        {
            "user": member,
            "team": team,
            "membership": membership,
            "domain": site.domain,
        },
    )
    to_email = member.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()


def notify_membership_confirmed(team, member, membership, site):
    notify_member_change(team, member, membership, site, "confirmed")


def notify_membership_rejected(team, member, membership, site):
    notify_member_change(team, member, membership, site, "rejected")


def add_areas_to_team(team, areas):
    valid_types = Area.AREA_TYPES.keys()
    country = None

    for area in areas.values():
        if area["type"] in valid_types:
            if country is None and area.get("country", None) is not None:
                country = {"code": area["country"], "name": area["country_name"]}

            area_code = area["codes"].get("gss", area["codes"].get("ons", None))

            if area_code is None:
                continue

            a, _ = Area.objects.update_or_create(
                area_type=area["type"],
                code=area_code,
                defaults={"name": area["name"], "mapit_id": area["id"]},
            )

            team.areas.add(a)

    if country is not None:
        a, _ = Area.objects.update_or_create(
            area_type="COUNTRY",
            code=country["code"],
            name=country["name"],
        )
        team.areas.add(a)
