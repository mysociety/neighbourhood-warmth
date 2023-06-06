from django.contrib.auth import get_user_model, login
from django.contrib.gis.geos import Point
from django.shortcuts import redirect, render, reverse
from django.urls import reverse
from django.views.generic import DetailView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

from neighbourhood.example_data import example_streets, example_teams
from neighbourhood.forms import JoinTeamForm, NewTeamForm
from neighbourhood.mixins import StreetMixin, TeamMixin, TitleMixin
from neighbourhood.models import Membership, Team, User
from neighbourhood.tokens import get_user_for_token
from neighbourhood.utils import find_where, get_postcode_centroid


class HomePageView(TitleMixin, TemplateView):
    template_name = "neighbourhood/home.html"


class SearchView(TitleMixin, TemplateView):
    page_title = "Find a team near you"
    template_name = "neighbourhood/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        postcode = self.request.GET.get("pc", None)
        context["postcode"] = postcode

        if postcode is None or postcode == "":
            context["error"] = "Please provide a postcode"
            return context

        lat_lon = get_postcode_centroid(postcode)
        if "error" in lat_lon:
            context["error"] = lat_lon["error"]
        else:
            nearest = Team.find_nearest_teams(
                latitude=lat_lon["lat"], longitude=lat_lon["lon"]
            )
            context["teams"] = nearest

        return context


class TeamView(TitleMixin, DetailView):
    model = Team
    queryset = Team.objects.filter(confirmed=True)
    context_object_name = "team"
    page_title = "Team profile"
    template_name = "neighbourhood/team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team = context["team"]
        user = self.request.user
        if not user.is_anonymous:
            membership = Membership.objects.filter(
                user=user, team=team
            ).first()
            if membership is not None:
                context["is_team_applicant"] = not membership.confirmed
                context["is_team_member"] = membership.confirmed
                context["is_team_admin"] = membership.is_admin

            context["member_count"] = Membership.objects.filter(
                team=team, confirmed=True
            ).count()
            context["applicant_count"] = Membership.objects.filter(
                team=team, confirmed=False
            ).count()

        return context


class CreateTeamView(TitleMixin, CreateView):
    page_title = "Create a team"
    form_class = NewTeamForm
    template_name = "neighbourhood/create_team.html"

    def get_initial(self):
        return {"base_pc": self.request.GET.get("pc", "")}

    def form_valid(self, form):
        data = form.cleaned_data

        um = get_user_model()
        u, _ = um.objects.get_or_create(email=data["email"])
        u.full_name = data["creator_name"]
        u.save()

        form.instance.creator = u

        location = Point(form.lat_lon["lon"], form.lat_lon["lat"], srid=4326)
        form.instance.centroid = location
        form.instance.status = "Newly created"

        response = super().form_valid(form)

        # add to members too as makes counting easier
        Membership.objects.create(
            team=form.instance, user=u, confirmed=True, is_admin=True
        )

        form.send_confirmation_email(request=self.request, user=u)

        return response

    def get_success_url(self):
        return reverse("confirmation_sent")


class JoinTeamView(TitleMixin, UpdateView):
    page_title = "Create a team"
    form_class = JoinTeamForm
    template_name = "neighbourhood/join_team.html"
    context_object_name = "team"

    def get_object(self):
        return Team.objects.get(slug=self.kwargs["slug"])

    def form_valid(self, form):
        data = form.cleaned_data

        um = get_user_model()
        u, _ = um.objects.get_or_create(email=data["email"])
        u.full_name = data["name"]
        u.save()

        response = super().form_valid(form)

        Membership.objects.create(team=form.instance, user=u)

        form.send_confirmation_email(request=self.request, user=u)

        return response

    def get_success_url(self):
        return reverse("confirmation_sent")


class ConfirmJoinTeamView(TitleMixin, DetailView):
    model = Team
    queryset = Team.objects.filter(confirmed=True)
    context_object_name = "team"
    page_title = "Confirm new members"
    template_name = "neighbourhood/confirm_join_team.html" # template doesn’t exist

    # TODO: Include a form for approving join requests for the given team.
    # TODO: Send email to applicant when their request is approved.


class StreetView(StreetMixin, TitleMixin, TemplateView):
    page_title = "Example Avenue"
    template_name = "neighbourhood/street.html"


class StreetJoinView(StreetMixin, TitleMixin, TemplateView):
    page_title = "Join | Example Avenue"
    template_name = "neighbourhood/street_join.html"


class StreetActionsView(StreetMixin, TitleMixin, TemplateView):
    page_title = "Actions | Example Avenue"
    template_name = "neighbourhood/street_actions.html"


class StreetUpdateView(StreetMixin, TitleMixin, TemplateView):
    page_title = "Update | Example Avenue"
    template_name = "neighbourhood/street_update.html"


class AreaView(TitleMixin, TemplateView):
    page_title = "Exampleshire County Council"
    template_name = "neighbourhood/area.html"


class AboutView(TitleMixin, TemplateView):
    page_title = "About"
    template_name = "neighbourhood/about.html"


class ConfirmEmailView(TitleMixin, TemplateView):
    page_title = "Email Confirmation"
    template_name = "neighbourhood/accounts/email_confirmation.html"

    def get(self, request, token=None):
        if token is not None:
            t, user = get_user_for_token(token)
            if t is None or user is None:
                return redirect(reverse("bad_token"))

            if not user.email_confirmed:
                user.email_confirmed = True
                user.save()

            # just log them in
            login(request, user)

            if t.domain == "new_team":
                team = Team.objects.get(id=t.domain_id)
                team.confirmed = True
                team.save()
                return redirect(reverse("team", args=(team.slug,)))
            elif t.domain == "join_team":
                team = Team.objects.get(id=t.domain_id)
                # TODO: send member join request email notification to team organisers
                return redirect(reverse("team", args=(team.slug,)))

        return super().get(request)


class ConfirmationSentView(TitleMixin, TemplateView):
    page_title = "Verify your email"
    template_name = "neighbourhood/accounts/confirmation_sent.html"


class BadTokenView(TitleMixin, TemplateView):
    page_title = "Bad Token"
    template_name = "neighbourhood/accounts/bad_token.html"


class EmailView(TemplateView):
    def get_template_names(self):
        if self.kwargs["layout"] == "welcome":
            return "neighbourhood/email_welcome.html"
        elif self.kwargs["layout"] == "joined":
            return "neighbourhood/email_joined.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["street"] = find_where(
            example_streets, {"slug": self.request.GET.get("street", {})}
        )
        return context


class StyleView(TitleMixin, TemplateView):
    page_title = "Style preview"
    template_name = "neighbourhood/style.html"

    def get_context_data(self, **kwargs):  # pragma: no cover
        context = super().get_context_data(**kwargs)
        context["shades"] = [(i * 100) for i in range(1, 10)]
        context["colors"] = [
            "blue",
            "indigo",
            "purple",
            "pink",
            "red",
            "orange",
            "yellow",
            "green",
            "teal",
            "cyan",
            "gray",
        ]
        context["theme_colors"] = [
            "primary",
            "secondary",
            "success",
            "info",
            "warning",
            "danger",
            "light",
            "dark",
        ]
        context["button_styles"] = ["", "outline-"]
        context["heading_levels"] = range(1, 7)
        context["display_levels"] = range(1, 7)
        context["sizes"] = [
            "-sm",
            "",
            "-lg",
        ]

        return context
