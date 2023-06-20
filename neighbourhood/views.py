from django.contrib.auth import get_user_model, login
from django.contrib.gis.geos import Point
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse
from django.views.generic import DetailView, TemplateView, UpdateView
from django.views.generic.edit import CreateView, FormView

from neighbourhood.forms import (
    ApproveMembershipFormSet,
    JoinTeamForm,
    LoginLinkForm,
    NewTeamForm,
)
from neighbourhood.mixins import TitleMixin
from neighbourhood.models import Area, Membership, Team
from neighbourhood.services.teams import (
    add_areas_to_team,
    notify_membership_confirmed,
    notify_membership_rejected,
    notify_new_member,
)
from neighbourhood.tokens import get_user_for_token
from neighbourhood.utils import get_area_geometry, get_postcode_centroid


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
            membership = Membership.objects.filter(user=user, team=team).first()
            if membership is not None:
                context["is_team_applicant"] = not membership.confirmed
                context["is_team_member"] = membership.confirmed
                context["is_team_admin"] = membership.is_admin

            context["member_count"] = Membership.objects.filter(
                team=team, confirmed=True
            ).count()
            context["applicant_count"] = Membership.objects.filter(
                team=team, confirmed=False, rejected=False
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

        location = Point(
            form.postcode_data["wgs84_lon"], form.postcode_data["wgs84_lat"], srid=4326
        )
        form.instance.centroid = location
        form.instance.status = "Newly created"

        response = super().form_valid(form)

        # add to members too as makes counting easier
        Membership.objects.create(
            team=form.instance, user=u, confirmed=True, is_admin=True
        )

        add_areas_to_team(form.instance, form.postcode_data["areas"])

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


class ConfirmJoinTeamView(TitleMixin, UpdateView):
    model = Team
    queryset = Team.objects.filter(confirmed=True)
    context_object_name = "team"
    page_title = "Confirm new members"
    template_name = "neighbourhood/confirm_join_team.html"
    form_class = ApproveMembershipFormSet

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if user.is_anonymous:
            raise PermissionDenied

        if (
            user.is_superuser
            or Membership.objects.filter(user=user, team=obj, is_admin=True).exists()
        ):
            return obj

        raise PermissionDenied

    def get_success_url(self):
        return reverse("confirm_join_team", args=(self.get_object().slug,))

    def form_valid(self, form):
        form.save()
        site = get_current_site(self.request)
        for membership_form in form:
            data = membership_form.cleaned_data
            m = data["id"]
            if data["confirmed"]:
                notify_membership_confirmed(m.team, m.user, m, site)
            elif data["rejected"]:
                notify_membership_rejected(m.team, m.user, m, site)
        return super().form_valid(form)


class AreaView(TitleMixin, DetailView):
    model = Area
    context_object_name = "area"
    template_name = "neighbourhood/area.html"

    def get_object(self, **kwargs):
        return Area.objects.get(code=self.kwargs["gss"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = context["area"].name
        return context


class AreaJSON(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = Area.objects.get(code=kwargs["gss"])
        g = get_area_geometry(area.mapit_id)
        context["geometry"] = g

        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context["geometry"])


class AreaTeamJSON(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Team.objects.filter(areas__code=self.kwargs["gss"], confirmed=True)

        context["teams"] = teams

        return context

    def render_to_response(self, context, **response_kwargs):
        data = {
            "type": "FeatureCollection",
        }
        features = []
        for team in context["teams"]:
            print(team.centroid.coords)
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": team.centroid.coords,
                    },
                    "properties": {
                        "name": team.name,
                        "url": reverse("team", args=(team.slug,)),
                    },
                }
            )
        data["features"] = features
        return JsonResponse(data)


class AboutView(TitleMixin, TemplateView):
    page_title = "About"
    template_name = "neighbourhood/about.html"


class PrivacyView(TitleMixin, TemplateView):
    page_title = "Privacy policy"
    template_name = "neighbourhood/privacy.html"


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
                current_site = get_current_site(request)
                notify_new_member(team, user, current_site)
                return redirect(reverse("team", args=(team.slug,)))

        return super().get(request)


class ConfirmationSentView(TitleMixin, TemplateView):
    page_title = "Verify your email"
    template_name = "neighbourhood/accounts/confirmation_sent.html"


class BadTokenView(TitleMixin, TemplateView):
    page_title = "Bad Token"
    template_name = "neighbourhood/accounts/bad_token.html"


class LoginLinkView(TitleMixin, FormView):
    page_title = "Sign in"
    template_name = "neighbourhood/accounts/login_link.html"
    form_class = LoginLinkForm
    email_sent = False

    def form_valid(self, form):
        um = get_user_model()
        u = um.objects.get(email=form.cleaned_data["email"])
        form.send_login_link_email(request=self.request, user=u)
        # TODO: Should we handle the case where email fails to send?
        self.email_sent = True
        return render(self.request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email_sent"] = self.email_sent
        return context

    def get(self, request, token=None):
        if token is not None:
            t, user = get_user_for_token(token)
            if t is None or user is None:
                return redirect(reverse("bad_token"))

            if not user.email_confirmed:
                user.email_confirmed = True
                user.save()

            login(request, user)

            # TODO: Send them to their team page if it exists!
            return redirect(reverse("home"))

        return super().get(request)


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
