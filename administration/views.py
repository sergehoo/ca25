import base64
import io
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, UpdateView, CreateView
from matplotlib import pyplot as plt

from administration.models import Attendance, Session, Event
from public.models import User, BeToBe, Meeting, VisitCounter

User = get_user_model()


# Create your views here.
class AdminDah(TemplateView):
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


def scan_qr_code(request, slug):
    """ Gérer le scan du QR Code et rediriger correctement """

    session = get_object_or_404(Session, slug=slug)

    # Vérifier si la requête vient de l'application mobile
    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    is_mobile_app = "myapp" in user_agent  # Modifier avec l'User-Agent de ton app mobile

    if is_mobile_app:
        # Si l'utilisateur est connecté, enregistrer sa présence
        if request.user.is_authenticated:
            attendance, created = Attendance.objects.get_or_create(user=request.user, session=session)
            return JsonResponse({
                "message": "Présence confirmée.",
                "session": session.title,
                "already_registered": not created
            }, status=200)
        else:
            return JsonResponse({"error": "Authentification requise."}, status=401)

    # Si le scan est fait en dehors de l'application, rediriger vers l'App Store ou Google Play
    app_store_url = "https://apps.apple.com/app/id123456789"  # Lien de l'application iOS
    play_store_url = "https://play.google.com/store/apps/details?id=com.exemple.myapp"  # Lien Android

    if "android" in user_agent:
        return redirect(play_store_url)
    elif "iphone" in user_agent or "ipad" in user_agent:
        return redirect(app_store_url)

    # Redirection par défaut vers la page de téléchargement si autre navigateur
    return redirect("https://www.conferencedabidjan.com/app")


class SessionListView(ListView):
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
def generate_visit_chart():
    """ Génère un graphique des visites sur les 7 derniers jours. """
    last_week = now() - timedelta(days=7)
    visits_per_day = (
        VisitCounter.objects.filter(timestamp__gte=last_week)
        .extra({'day': "date(timestamp)"})
        .values('day')
        .annotate(total_visits=models.Count('id'))
        .order_by('day')
    )

    days = [entry['day'] for entry in visits_per_day]
    visit_counts = [entry['total_visits'] for entry in visits_per_day]

    # Générer le graphique
    plt.figure(figsize=(8, 4))
    plt.plot(days, visit_counts, marker="o", linestyle="-", color="blue", label="Visites")
    plt.xlabel("Date")
    plt.ylabel("Nombre de visites")
    plt.title("Nombre de visites par jour (7 derniers jours)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convertir l'image en base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    return graphic.decode("utf-8")

def dashboard_view(request):
    """ Vue du tableau de bord """
    visit_chart = generate_visit_chart()
    return render(request, "admin/dashboard.html", {"visit_chart": visit_chart})