"""
URL configuration for siade25 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from administration.views import AdminDah, ParticipantListView, ParticipantDetailView, EventListView, EventDetailView, \
    EventCreateView, EventDeleteView, EventUpdateView, SessionListView, SessionDetailView, SessionCreateView, \
    SessionUpdateView, SessionDeleteView, AttendanceListView, AttendanceDetailView, BeToBe, BetobeListview, \
    BetobeDetailview
from public.views import HomePageView

urlpatterns = [

                  path('dashboard', AdminDah.as_view(), name='dashboard'),
                  path('participant/liste/', ParticipantListView.as_view(), name='participant-list'),
                  path("participants/<int:pk>/", ParticipantDetailView.as_view(), name="participant-detail"),

                  # Événements
                  path("events/", EventListView.as_view(), name="event-list"),
                  path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
                  path("events/create/", EventCreateView.as_view(), name="event-create"),
                  path("events/<int:pk>/edit/", EventUpdateView.as_view(), name="event-edit"),
                  path("events/<int:pk>/delete/", EventDeleteView.as_view(), name="event-delete"),


                  path("rencontre/b2b/", BetobeListview.as_view(), name="rencontreb2b-list"),
                  path("rencontre/b2b/details/<int:pk>", BetobeDetailview.as_view(), name="rencontreb2b-details"),

                  # Sessions
                  path("sessions/", SessionListView.as_view(), name="session-list"),
                  path("sessions/<int:pk>/", SessionDetailView.as_view(), name="session-detail"),
                  path("sessions/create/", SessionCreateView.as_view(), name="session-create"),
                  path("sessions/<int:pk>/edit/", SessionUpdateView.as_view(), name="session-edit"),
                  path("sessions/<int:pk>/delete/", SessionDeleteView.as_view(), name="session-delete"),

                  # Présences
                  path("attendances/", AttendanceListView.as_view(), name="attendance-list"),
                  path("attendances/<int:pk>/", AttendanceDetailView.as_view(), name="attendance-detail"),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
