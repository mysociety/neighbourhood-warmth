import json

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.forms import (
    BaseModelFormSet,
    CharField,
    EmailField,
    FileField,
    Form,
    ModelForm,
    modelformset_factory,
)
from django.template.loader import render_to_string

from neighbourhood.models import Membership, Team, User
from neighbourhood.tokens import make_token_for_user
from neighbourhood.utils import get_postcode_data


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

        data = get_postcode_data(pc)
        if "error" in data:
            raise ValidationError(data["error"], code="invalid")

        self.postcode_data = data

        return pc

    def send_confirmation_email(self, request=None, user=None):
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
            raise ValidationError(
                "There is no user with that email address. Did you use a different address when signing up?"
            )

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


class ApproveMembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ["confirmed", "rejected", "is_admin"]


class BaseApproveMembershipFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        team = kwargs["instance"]
        del kwargs["instance"]
        super().__init__(*args, **kwargs)
        self.queryset = Membership.objects.filter(
            team=team,
            confirmed=False,
            rejected=False,
        )


ApproveMembershipFormSet = modelformset_factory(
    Membership,
    form=ApproveMembershipForm,
    edit_only=True,
    formset=BaseApproveMembershipFormSet,
    extra=0,
)


class PostcodeForm(Form):
    pc = CharField(max_length=20)

    def clean(self):
        pc = self.cleaned_data["pc"]
        data = get_postcode_data(pc)
        if data.get("error", None) is not None:
            raise ValidationError(data["error"])

        self.postcode_data = data


class GeoJsonUploadFormMixin(ModelForm):
    geojson_file = FileField(required=False, label="Upload GeoJSON")

    def clean_geojson_file(self):
        file = self.cleaned_data.get("geojson_file")
        if file:
            try:
                geojson_data = json.load(file)
                if geojson_data["type"] == "FeatureCollection":
                    feature = geojson_data["features"][0]
                elif geojson_data["type"] == "Feature":
                    feature = geojson_data
                else:
                    raise ValidationError(
                        "GeoJSON file must contain a single Feature or FeatureCollection."
                    )
                return GEOSGeometry(json.dumps(feature["geometry"]))
            except (KeyError, TypeError, json.JSONDecodeError):
                raise ValidationError("Invalid GeoJSON file format.")
        return None
