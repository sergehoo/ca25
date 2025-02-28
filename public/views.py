from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.generic import TemplateView

from administration.models import Session, Temoignage
from public.forms import MeetingForm, TemoignageForm, CommentForm
from public.models import Album, BlogPost, GuestarsSpeaker


def soumettre_temoignage(request):
    """ Vue pour enregistrer un témoignage soumis via AJAX """
    if request.method == "POST":
        form = TemoignageForm(request.POST)
        if form.is_valid():
            temoignage = form.save(commit=False)
            temoignage.statut = "En attente"  # Mise en attente de validation
            temoignage.save()
            return JsonResponse({"message": "Votre témoignage a été soumis avec succès !"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    return JsonResponse({"message": "Requête invalide"}, status=400)


# Create your views here.
class HomePageView(TemplateView):
    template_name = "public/public-page/home.html"

    def get_context_data(self, **kwargs):
        """ Ajoute la liste des participants à la session B2B """
        context = super().get_context_data(**kwargs)
        context["sessions"] = Session.objects.all()

        sessions = Session.objects.all().order_by('start_time')

        prochaine_session = Session.objects.filter(start_time__gte=now()).order_by('start_time').first()

        # Grouper les sessions par date
        sessions_par_jour = defaultdict(list)
        for session in sessions:
            sessions_par_jour[session.start_time.date()].append(session)

        context = {
            'sessions_par_jour': dict(sessions_par_jour),
            'prochaine_session': prochaine_session,
            'speakerguestars':GuestarsSpeaker.objects.select_related("user").all(),
            'albums': Album.objects.prefetch_related("photos").all(),
            'articles': BlogPost.objects.filter(status="published").order_by('-published_at')[:3],
            'temoignages': Temoignage.objects.filter(statut="Validé").order_by('-date_soumission')[:10]
        }

        return context


@login_required
def create_meeting(request):
    if request.user.role != "participant":
        messages.error(request, "Seuls les participants peuvent créer des rencontres.")
        return redirect("/")

    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.participant = request.user
            meeting.save()
            messages.success(request, "Votre rencontre a été enregistrée avec succès !")
            return redirect("meeting-list")
    else:
        form = MeetingForm(initial={"participant": request.user})

    return render(request, "meetings/create_meeting.html", {"form": form})


def soumettre_temoignage(request):
    if request.method == "POST":
        form = TemoignageForm(request.POST)
        if form.is_valid():
            temoignage = form.save(commit=False)
            temoignage.save()
            messages.success(request,
                             "Votre témoignage a été soumis avec succès et sera examiné par un administrateur.")
            return redirect('temoignages_list')  # Rediriger vers la page des témoignages
    else:
        form = TemoignageForm()

    return render(request, "temoignages/soumettre_temoignage.html", {"form": form})


def blog_list(request):
    """ Vue qui affiche les articles du blog """
    articles = BlogPost.objects.filter(status="published").order_by('-published_at')[
               :3]  # Récupérer les 3 derniers articles
    return render(request, 'blog_list.html', {'articles': articles})


def blog_detail(request, slug):
    """ Vue qui affiche les détails d’un article """
    article = get_object_or_404(BlogPost, slug=slug, status="published")
    comments = article.comments.filter(approved=True)
    comment_form = CommentForm()

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = article
            comment.save()

    return render(request, 'blog/blog_detail.html',
                  {'article': article, 'comments': comments, 'comment_form': comment_form})


class PolitiqueConfidentialiteView(TemplateView):
    template_name = "public/public-page/politique.html"
