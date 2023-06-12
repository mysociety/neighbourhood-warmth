from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from neighbourhood.models import Team


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
