"""neighbourhood_warmth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from neighbourhood import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search_results"),
    path("team/<slug:slug>/", views.TeamView.as_view(), name="team"),
    path("team/<slug:slug>/join/", views.JoinTeamView.as_view(), name="join_team"),
    path(
        "team/<slug:slug>/confirm/",
        views.ConfirmJoinTeamView.as_view(),
        name="confirm_join_team",
    ),
    path("create_team/", views.CreateTeamView.as_view(), name="create_team"),
    path("area/<slug:gss>/", views.AreaView.as_view(), name="area"),
    path("about/", views.AboutView.as_view(), name="about"),
    path(
        "email-preview/<slug:layout>/", views.EmailView.as_view(), name="email_preview"
    ),
    path(
        "confirmation_sent/",
        views.ConfirmationSentView.as_view(),
        name="confirmation_sent",
    ),
    path(
        "bad_token/",
        views.BadTokenView.as_view(),
        name="bad_token",
    ),
    re_path(
        "activate/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/",
        views.ConfirmEmailView.as_view(),
        name="confirm_email",
    ),
    re_path(
        "login-link/((?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,40})/)?",
        views.LoginLinkView.as_view(),
        name="login_link",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("style/", views.StyleView.as_view(), name="style"),
    path("impersonate/", include('impersonate.urls')),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
