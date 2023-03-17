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
from django.contrib import admin
from django.urls import path
from neighbourhood import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("search/", views.DisambiguationView.as_view(), name="search_results"),
    path("street/<slug:street>/", views.StreetView.as_view(), name="street"),
    path("street/<slug:street>/join/", views.StreetJoinView.as_view(), name="street_join"),
    path("street/<slug:street>/actions/", views.StreetActionsView.as_view(), name="street_actions"),
    path("street/<slug:street>/update/", views.StreetUpdateView.as_view(), name="street_update"),
    path("area/<slug:gss>/", views.AreaView.as_view(), name="area"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("email-preview/<slug:layout>/", views.EmailView.as_view(), name="email_preview"),
    path("style/", views.StyleView.as_view(), name="style"),
    path("admin/", admin.site.urls),
]
