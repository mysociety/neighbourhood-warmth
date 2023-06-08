from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.forms import (CharField, EmailField, HiddenInput, ModelForm,
                          Textarea, TextInput)
from django.template.loader import render_to_string

from neighbourhood.models import Team, User
from neighbourhood.tokens import make_token_for_user
from neighbourhood.utils import get_postcode_centroid


class NewTeamForm(ModelForm):
    email = EmailField(
        label="Your email address", help_text="This won’t be shared with anyone"
    )
    creator_name = CharField(
        label="Your name",
        help_text="This will only ever be shared with other members of your team",
    )

    def clean_base_pc(self):
        data = self.cleaned_data
        pc = data["base_pc"]

        lat_lon = get_postcode_centroid(pc)
        if "error" in lat_lon:
            raise ValidationError(lat_lon["error"], code="invalid")

        self.lat_lon = lat_lon

        return pc

    def send_confirmation_email(self, request=None, user=None):
        print(self.instance)
        t = make_token_for_user(user, domain="new_team", obj=self.instance)

        current_site = get_current_site(request)
        mail_subject = render_to_string(
            "neighbourhood/accounts/confirmation_email_subject.txt"
        ).strip()
        message = render_to_string(
            "neighbourhood/accounts/confirmation_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "token": t.token,
            },
        )
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

    class Meta:
        model = Team
        fields = ["name", "base_pc", "address_1", "address_2", "address_3"]
        labels = {
            "address_1": "Address line 1",
            "address_2": "Address line 2",
            "address_3": "Address line 3",
            "base_pc": "Postcode",
            "name": "Team name",
        }


class JoinTeamForm(ModelForm):
    email = EmailField(
        label="Your email address", help_text="This won’t be shared with anyone"
    )
    name = CharField(
        label="Your name",
        help_text="This will only ever be shared with other members of your team",
    )

    def send_confirmation_email(self, request=None, user=None):
        print(self.instance)
        t = make_token_for_user(user, domain="join_team", obj=self.instance)

        current_site = get_current_site(request)
        mail_subject = render_to_string(
            "neighbourhood/accounts/confirmation_email_subject.txt"
        ).strip()
        message = render_to_string(
            "neighbourhood/accounts/confirmation_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "token": t.token,
            },
        )
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

    class Meta:
        fields = []
        model = Team


class LoginLinkForm(ModelForm):
    def clean(self):
        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            return self.cleaned_data
        else:
            raise ValidationError('There is no user with that email address. Did you use a different address when signing up?')

    def send_login_link_email(self, request=None, user=None):
        t = make_token_for_user(user, domain="login", obj=self.instance)
        current_site = get_current_site(request)
        mail_subject = render_to_string(
            "neighbourhood/accounts/login_link_email_subject.txt"
        ).strip()
        message = render_to_string(
            "neighbourhood/accounts/login_link_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "token": t.token,
            },
        )
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

    class Meta:
        model = User
        fields = ["email"]
