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
