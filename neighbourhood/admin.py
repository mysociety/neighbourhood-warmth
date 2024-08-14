from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html, mark_safe

from .models import Challenge, Team, Token, User


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ["token", "domain", "user_id", "domain_id"]
    list_filter = ["domain"]


class TeamMembershipInline(admin.TabularInline):
    model = Team.members.through
    readonly_fields = ["created"]


@admin.register(Team)
class TeamAdmin(OSMGeoAdmin):
    list_display = (
        "name",
        "base_pc",
        "members_count",
        "confirmed_members_count",
        "status",
        "created",
    )
    list_filter = ["status", "created"]
    readonly_fields = ["created"]
    inlines = [
        TeamMembershipInline,
    ]

    @admin.display(description="Members")
    def members_count(self, obj):
        return obj.members.count()

    @admin.display(description="Confirmed members")
    def confirmed_members_count(self, obj):
        return obj.confirmed_members.count()


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ["is_active", "has_rich_description"]
    ordering = ["order"]


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email", "full_name"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "full_name",
            "is_superuser",
            "is_active",
            "is_staff",
        ]


class UserMembershipInline(admin.TabularInline):
    model = User.teams.through
    readonly_fields = ["created"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = [
        "email",
        "full_name",
        "is_active",
        "email_confirmed",
        "is_staff",
        "date_joined",
        "team_names",
    ]
    list_filter = ["is_active", "email_confirmed", "is_staff", "date_joined"]
    readonly_fields = ["date_joined"]
    fieldsets = [
        (None, {"fields": ["email", "password", "full_name", "date_joined"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                ]
            },
        ),
    ]
    inlines = [
        UserMembershipInline,
    ]

    @admin.display(description="Teams")
    def team_names(self, obj):
        links = []
        for team in obj.teams.all():
            url = reverse(
                "admin:{}_{}_change".format(
                    Team._meta.app_label, Team._meta.model_name
                ),
                args=(team.pk,),
            )
            html = format_html(
                '<a href="{url}">{text}</a>'.format(url=url, text=team.name)
            )
            links.append(html)
        return mark_safe(", ".join(links))

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ["groups", "user_permissions"]


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
