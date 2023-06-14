from django.core.mail import EmailMessage
from django.template.loader import render_to_string


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
