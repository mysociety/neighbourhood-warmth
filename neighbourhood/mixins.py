from neighbourhood.example_data import example_streets, example_teams
from neighbourhood.utils import find_where


class StreetMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["street"] = find_where(example_streets, {"slug": self.kwargs["street"]})
        return context


class TeamMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = find_where(example_teams, {"slug": self.kwargs["team"]})
        return context


class TitleMixin:
    site_title = "Neighbourhood Warmth"

    def get_page_title(self):
        try:
            if self.page_title:
                return f"{self.page_title} | {self.site_title}"
        except AttributeError:
            pass

        return f"{self.site_title}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title()
        return context
