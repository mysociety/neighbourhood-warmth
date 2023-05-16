from django.core.exceptions import ValidationError
from django.forms import (CharField, EmailField, HiddenInput, ModelForm,
                          Textarea, TextInput)

from neighbourhood.models import Team
from neighbourhood.utils import get_postcode_centroid


class NewTeamForm(ModelForm):
    email = EmailField()
    creator_name = CharField()

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
