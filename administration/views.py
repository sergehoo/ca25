from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, UpdateView, CreateView

from administration.models import Attendance, Session, Event
from public.models import User, BeToBe, Meeting

User = get_user_model()


# Create your views here.
class AdminDah( TemplateView):
    template_name = "administration/admin-page/dashboard.html"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class ParticipantListView(UserPassesTestMixin, ListView):
    model = User
    template_name = "administration/admin-page/participant-list.html"
    context_object_name = "participants"
    paginate_by = 10  # Paginer la liste des participants

    # def get_queryset(self):
    #     return User.objects.filter(role="participant")  # Filtrer uniquement les participants
    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class ParticipantDetailView(UserPassesTestMixin, DetailView):
    model = User
    template_name = "administration/admin-page/participant-detail.html"
    context_object_name = "participant"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class EventListView(UserPassesTestMixin, ListView):
    model = Event
    template_name = "events/event-list.html"
    context_object_name = "events"
    paginate_by = 10

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class EventDetailView(UserPassesTestMixin, DetailView):
    model = Event
    template_name = "events/event-detail.html"
    context_object_name = "event"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class EventCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Event
    template_name = "events/event-form.html"
    fields = ["name", "description", "start_date", "end_date", "location"]
    success_url = reverse_lazy("event-list")

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class EventUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Event
    template_name = "events/event-form.html"
    fields = ["name", "description", "start_date", "end_date", "location"]
    success_url = reverse_lazy("event-list")

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class EventDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Event
    template_name = "events/event-confirm-delete.html"
    success_url = reverse_lazy("event-list")

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


@login_required
def scan_qr_code(request, slug):
    # Récupérer la session correspondant au slug du QR code
    session = get_object_or_404(Session, slug=slug)

    # Vérifier si l'utilisateur est déjà enregistré pour cette session
    attendance, created = Attendance.objects.get_or_create(user=request.user, session=session)

    if created:
        messages.success(request, f"Votre présence à la session '{session.title}' a été confirmée ! ✅")
    else:
        messages.warning(request, f"Vous avez déjà scanné le QR Code pour cette session. ⚠")

    return redirect("session-detail", pk=session.pk)


class SessionListView( ListView):
    model = Session
    template_name = "administration/admin-page/session-list.html"
    context_object_name = "sessions"
    paginate_by = 10

    def get_queryset(self):
        return Session.objects.annotate(participant_count=Count("attendances"))

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class SessionDetailView(UserPassesTestMixin, DetailView):
    model = Session
    template_name = "sessions/session-detail.html"
    context_object_name = "session"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class SessionCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Session
    template_name = "sessions/session-form.html"
    fields = ["event", "title", "description", "start_time", "end_time"]
    success_url = reverse_lazy("session-list")

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class SessionUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Session
    template_name = "sessions/session-form.html"
    fields = ["title", "description", "start_time", "end_time"]
    success_url = reverse_lazy("session-list")

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class SessionDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Session
    template_name = "sessions/session-confirm-delete.html"
    success_url = reverse_lazy("session-list")

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class AttendanceListView(UserPassesTestMixin, ListView):
    model = Attendance
    template_name = "attendance/attendance-list.html"
    context_object_name = "attendances"
    paginate_by = 10

    def get_queryset(self):
        return Attendance.objects.select_related("user", "session").order_by("-scanned_at")

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class AttendanceDetailView(UserPassesTestMixin, DetailView):
    model = Attendance
    template_name = "attendance/attendance-detail.html"
    context_object_name = "attendance"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")


class BetobeListview(UserPassesTestMixin, ListView):
    model = BeToBe
    context_object_name = "btob"
    paginate_by = 10
    template_name = "administration/admin-page/rencontre_b2b.html"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")

    def get_queryset(self):
        """ Ajoute une propriété `expired` aux sessions pour indiquer si elles sont terminées """
        queryset = super().get_queryset().select_related("sponsor")
        BeToBe.objects.annotate(meeting_count=Count("meetings")).select_related("sponsor")
        return queryset


class BetobeDetailview(UserPassesTestMixin, DetailView):
    model = BeToBe
    context_object_name = "btobdetails"
    template_name = "administration/admin-page/rencontre_b2b_detail.html"

    def test_func(self):
        """ Vérifie que l'utilisateur est un organisateur """
        return self.request.user.is_authenticated and self.request.user.role == "organisateur"

    def handle_no_permission(self):
        """ Redirige vers la page d'accueil si l'utilisateur n'est pas un organisateur """
        return redirect("home")

    def get_context_data(self, **kwargs):
        """ Ajoute la liste des participants à la session B2B """
        context = super().get_context_data(**kwargs)
        context["participants"] = Meeting.objects.filter(btob=self.object).select_related("participant")
        return context
