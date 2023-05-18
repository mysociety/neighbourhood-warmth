from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView

from neighbourhood.example_data import example_streets, example_teams
from neighbourhood.forms import NewTeamForm
from neighbourhood.mixins import StreetMixin, TeamMixin, TitleMixin
from neighbourhood.models import Team, User
from neighbourhood.utils import find_where, get_postcode_centroid


class HomePageView(TitleMixin, TemplateView):
    template_name = "neighbourhood/home.html"


class SearchView(TitleMixin, TemplateView):
    page_title = "Find a team near you"
    template_name = "neighbourhood/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        postcode = self.request.GET.get("pc")

        context["postcode"] = postcode
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
    context_object_name = "team"
    page_title = "Team profile"
    template_name = "neighbourhood/team.html"


class CreateTeamView(TitleMixin, CreateView):
    page_title = "Create a team"
    form_class = NewTeamForm
    template_name = "neighbourhood/create_team.html"
    success_url = "/team/halton-park-heroes-100003/"

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
        form.instance.members.add(u)

        return response

    def get_success_url(self):
        return reverse("team", args=(self.object.slug,))


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
