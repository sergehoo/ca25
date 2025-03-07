from allauth.account.utils import complete_signup
from dj_rest_auth.registration.views import RegisterView
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from administration.api.serializers import BeToBeSerializer, MeetingSerializer, CustomRegisterSerializer, \
    UserSerializer, AlbumSerializer, PhotoSerializer, CategorySerializer, BlogPostSerializer, CommentSerializer, \
    GuestarsSpeakerSerializer, AttendanceSerializer, TemoignageSerializer, SessionSerializer, UserProfileSerializer, \
    RegisterSerializer, LikeTemoignageSerializer, AvisSerializer
from administration.models import Attendance, Session, Temoignage, LikeTemoignage, Avis
from public.models import BeToBe, Meeting, Album, Photo, Category, BlogPost, Comment, GuestarsSpeaker, Profile
from allauth.account import app_settings as allauth_settings


# @method_decorator(csrf_exempt, name="dispatch")
# class CustomRegisterViewSet(viewsets.ViewSet):
#     """ ViewSet personnalisé pour l'inscription des utilisateurs avec Django Allauth et DRF """
#
#     permission_classes = [AllowAny]  # ✅ Autoriser tout le monde
#
#     @action(detail=False, methods=["post"])
#     def register(self, request):
#         """ Gestion de l'inscription des utilisateurs """
#         serializer = CustomRegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save(request)
#             complete_signup(
#                 request._request, user, allauth_settings.EMAIL_VERIFICATION, None
#             )
#             return Response(
#                 {"message": "Inscription réussie. Veuillez vérifier votre email pour activer votre compte."},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     # def validate_email(self, email):
#     #     if User.objects.filter(email=email).exists():
#     #         raise serializers.ValidationError("Cet email est déjà utilisé.")
#     #     return email


# class CustomRegisterView(RegisterView):
#     """ Vue d'inscription personnalisée """
#
#     serializer_class = CustomRegisterSerializer
#
#     def form_valid(self, form):
#         """ Ajout d'un message de confirmation """
#         response = super().form_valid(form)
#         return Response(
#             {"message": "Inscription réussie. Veuillez vérifier votre email pour activer votre compte."},
#             status=status.HTTP_201_CREATED
#         )
#
#     def form_invalid(self, form):
#         """ Gestion des erreurs de validation """
#         return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def options(self, request, *args, **kwargs):
#         """ Répond avec les méthodes autorisées """
#         response = super().options(request, *args, **kwargs)
#         response["Allow"] = "POST, OPTIONS"
#         return response
#
#     def get(self, request, *args, **kwargs):
#         """ Bloque les requêtes GET et affiche un message d’erreur """
#         return JsonResponse({"error": "GET method not allowed. Use POST."}, status=405)

class RegisterView(APIView):
    """ API pour l'inscription des utilisateurs """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # ✅ Retourner un token JWT immédiatement après l'inscription (optionnel)
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Utilisateur créé avec succès !",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvisListCreateView(generics.ListCreateAPIView):
    """
    Liste et création de commentaires pour une session spécifique
    """
    serializer_class = AvisSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return Avis.objects.filter(session_id=session_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """ API pour récupérer, créer, mettre à jour et supprimer le profil utilisateur """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ Seul l'utilisateur connecté peut gérer son profil

    def get_object(self):
        """ 🔍 Récupérer le profil de l'utilisateur connecté ou lever une erreur """
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise NotFound({"error": "Profil introuvable"})

    def get(self, request, *args, **kwargs):
        """ 📌 Récupère le profil de l'utilisateur connecté """
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ 📌 Crée un profil pour l'utilisateur s'il n'existe pas """
        if Profile.objects.filter(user=request.user).exists():
            return Response({"error": "Le profil existe déjà"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """ 📌 Met à jour complètement le profil """
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """ 📌 Mise à jour partielle du profil """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """ 📌 Supprime le profil utilisateur """
        return self.destroy(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """ Vue pour changer le mot de passe """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Ancien mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Mot de passe mis à jour avec succès"}, status=status.HTTP_200_OK)


class BeToBeViewSet(viewsets.ModelViewSet):
    queryset = BeToBe.objects.all()
    serializer_class = BeToBeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """ Surcharge la méthode `list` pour s'assurer que la réponse est un tableau """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # 🔍 S'assure que la réponse est bien une liste `[]`


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """ Surcharge la méthode `list` pour s'assurer que la réponse est un tableau """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # 🔍 S'assure que la réponse est bien une liste `[]`


# class MeetingViewSet(viewsets.ModelViewSet):
#     """ Gestion des rendez-vous entre participants et sponsors """
#     queryset = Meeting.objects.all()
#     serializer_class = MeetingSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(participant=self.request.user)


class AlbumViewSet(viewsets.ModelViewSet):
    """ Gestion des albums photos """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    # permission_classes = [IsAuthenticated]


class PhotoViewSet(viewsets.ModelViewSet):
    """ Gestion des photos dans les albums """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    # permission_classes = [IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    """ Gestion des catégories d'articles """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Tout le monde peut voir les catégories


class BlogPostViewSet(viewsets.ModelViewSet):
    """ Gestion des articles de blog """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ Gestion des commentaires sur les articles """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]  # Les commentaires peuvent être créés sans authentification


class GuestarsSpeakerViewSet(viewsets.ModelViewSet):
    """ Gestion des intervenants """
    queryset = GuestarsSpeaker.objects.all()
    serializer_class = GuestarsSpeakerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionViewSet(viewsets.ModelViewSet):
    """ API CRUD pour les sessions """
    queryset = Session.objects.all().prefetch_related("avis", "speaker")
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AttendanceViewSet(viewsets.ModelViewSet):
    """ API CRUD pour l'enregistrement des présences """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    # permission_classes = [IsAuthenticated]
    @action(detail=False, methods=["post"])
    def scan_qr(self, request):
        """ API pour scanner un QR Code et enregistrer une présence """

        slug = request.data.get("slug")
        session = get_object_or_404(Session, slug=slug)

        # 📌 Vérifier si l'utilisateur a déjà scanné ce QR Code
        if Attendance.objects.filter(user=request.user, session=session).exists():
            return Response({
                "message": "Vous êtes déjà enregistré pour cette session.",
                "status": "already_registered"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Enregistrer la présence
        attendance = Attendance.objects.create(user=request.user, session=session)

        return Response({
            "message": f"Votre présence à la session '{session.title}' a été confirmée.",
            "status": "success",
            "attendance": AttendanceSerializer(attendance).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def scan_redirect(self, request, slug=None):
        """
        Gère le scan d'un QR code hors de l'application.
        Si l'utilisateur scanne via un navigateur web, redirige vers l'application mobile ou le store.
        """

        session = get_object_or_404(Session, slug=slug)

        # 📌 Vérifier l'origine du scan (navigateur ou application)
        user_agent = request.headers.get("User-Agent", "").lower()
        is_mobile = "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent

        if is_mobile:
            # ✅ Générer un **Lien Profond** pour ouvrir directement l’application mobile
            deep_link = f"conferenceca://scan/{slug}"
            return Response({"redirect_url": deep_link}, status=status.HTTP_302_FOUND)

        else:
            # 🚨 **Redirection vers le store** si le scan est fait depuis un navigateur
            store_link = "https://play.google.com/store/apps/details?id=com.conferencedabidjan.app"
            return Response({"redirect_url": store_link}, status=status.HTTP_302_FOUND)
    # @action(detail=False, methods=["post"])
    # def scan_qr(self, request):
    #     """ API pour scanner un QR Code et enregistrer une présence """
    #
    #     slug = request.data.get("slug")
    #     session = get_object_or_404(Session, slug=slug)
    #
    #     # Vérifier si l'utilisateur est déjà enregistré
    #     if Attendance.objects.filter(user=request.user, session=session).exists():
    #         return Response({"message": "Vous êtes déjà enregistré pour cette session."},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #
    #     # Enregistrer la présence
    #     attendance = Attendance.objects.create(user=request.user, session=session)
    #     return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)


class ToggleLikeTemoignageView(generics.GenericAPIView):
    serializer_class = LikeTemoignageSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, temoignage_id):
        temoignage = get_object_or_404(Temoignage, id=temoignage_id)
        like, created = LikeTemoignage.objects.get_or_create(user=request.user, temoignage=temoignage)

        if not created:
            like.delete()
            return Response({"message": "Like retiré", "like_count": temoignage.like_count()}, status=status.HTTP_200_OK)

        return Response({"message": "Témoignage liké", "like_count": temoignage.like_count()}, status=status.HTTP_201_CREATED)


class TemoignageViewSet(viewsets.ModelViewSet):
    """ API CRUD pour les témoignages """
    queryset = Temoignage.objects.all()
    serializer_class = TemoignageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Temoignage.objects.all()  # Admin voit tout
        return Temoignage.objects.filter(statut='Validé')  # Utilisateurs voient seulement les témoignages validés

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def valider(self, request, pk=None):
        """ Valider un témoignage """
        temoignage = self.get_object()
        temoignage.statut = "Validé"
        temoignage.date_validation = now()
        temoignage.save()
        return Response({"message": "Témoignage validé."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def rejeter(self, request, pk=None):
        """ Rejeter un témoignage """
        temoignage = self.get_object()
        temoignage.statut = "Rejeté"
        temoignage.save()
        return Response({"message": "Témoignage rejeté."}, status=status.HTTP_200_OK)
