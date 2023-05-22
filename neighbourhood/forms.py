from django.core.exceptions import ValidationError
from django.forms import (CharField, EmailField, HiddenInput, ModelForm,
                          Textarea, TextInput)

from neighbourhood.models import Team
from neighbourhood.utils import get_postcode_centroid


class NewTeamForm(ModelForm):
    email = EmailField(
        label="Your email address",
        help_text="This won’t be shared with anyone"
    )
    creator_name = CharField(
        label="Your name",
        help_text="This will only ever be shared with other members of your team"
    )

    def clean_base_pc(self):
        data = self.cleaned_data
        pc = data["base_pc"]

        lat_lon = get_postcode_centroid(pc)
        if "error" in lat_lon:
            raise ValidationError(lat_lon["error"], code="invalid")

        self.lat_lon = lat_lon

        return pc

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
