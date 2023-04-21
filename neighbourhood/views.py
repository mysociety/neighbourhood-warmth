from django.shortcuts import render

from django.views.generic import TemplateView

from neighbourhood.mixins import StreetMixin, TeamMixin, TitleMixin
from neighbourhood.example_data import example_streets, example_teams
from neighbourhood.utils import find_where


class HomePageView(TitleMixin, TemplateView):
    template_name = "neighbourhood/home.html"


class SearchView(TitleMixin, TemplateView):
    page_title = "Find a team near you"
    template_name = "neighbourhood/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = example_teams
        return context


class TeamView(TeamMixin, TitleMixin, TemplateView):
    page_title = "Team profile"
    template_name = "neighbourhood/team.html"


class CreateTeamView(TitleMixin, TemplateView):
    page_title = "Create a team"
    template_name = "neighbourhood/create_team.html"


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
            example_streets,
            {
                "slug": self.request.GET.get("street", {})
            }
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
