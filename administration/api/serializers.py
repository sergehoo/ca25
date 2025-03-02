import uuid
from io import BytesIO

import qrcode
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files import File
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer

from administration.models import Event, Session, Attendance, Temoignage
from public.models import BeToBe, Meeting, Photo, Album, User, Profile, Category, BlogPost, Comment, GuestarsSpeaker


# class CustomRegisterSerializer(RegisterSerializer):
#     nom = serializers.CharField(required=True)
#     prenom = serializers.CharField(required=True)
#     email = serializers.EmailField(required=True)
#     contact = serializers.CharField(required=False, allow_blank=True)
#     role = serializers.ChoiceField(choices=User.ROLES, required=True)
#     fonction = serializers.CharField(required=False, allow_blank=True)
#     company = serializers.CharField(required=False, allow_blank=True)
#     sector = serializers.CharField(required=False, allow_blank=True)
#
#     def validate_email(self, email):
#         """ Vérifie que l'email est unique """
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
#         return email
#
#     def get_cleaned_data(self):
#         """ Récupère les données nettoyées avant la création de l'utilisateur """
#         data = super().get_cleaned_data()
#         data.update({
#             "nom": self.validated_data.get("nom", ""),
#             "prenom": self.validated_data.get("prenom", ""),
#             "contact": self.validated_data.get("contact", ""),
#             "role": self.validated_data.get("role", ""),
#             "fonction": self.validated_data.get("fonction", ""),
#             "company": self.validated_data.get("company", ""),
#             "sector": self.validated_data.get("sector", ""),
#         })
#         return data


UserModel = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    nom = serializers.CharField(required=True)
    prenom = serializers.CharField(required=True)
    contact = serializers.CharField(required=False, allow_blank=True)
    civilite = serializers.ChoiceField(choices=User.CIVILITE_CHOICES, required=False)
    role = serializers.ChoiceField(choices=User.ROLES, required=False)
    fonction = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    sector = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return email

    def get_cleaned_data(self):
        """
        Récupère les champs supplémentaires fournis par l'utilisateur
        """
        return {
            "nom": self.validated_data.get("nom", ""),
            "prenom": self.validated_data.get("prenom", ""),
            "contact": self.validated_data.get("contact", ""),
            "civilite": self.validated_data.get("civilite", ""),
            "role": self.validated_data.get("role", ""),
            "fonction": self.validated_data.get("fonction", ""),
            "company": self.validated_data.get("company", ""),
            "sector": self.validated_data.get("sector", ""),
            "description": self.validated_data.get("description", ""),
        }

    def save(self, request):
        """
        🔹 Créer l'utilisateur manuellement pour s'assurer que tous les champs sont enregistrés
        """
        user = UserModel.objects.create_user(
            email=self.validated_data.get("email"),
            password=self.validated_data.get("password1"),
            nom=self.validated_data.get("nom", ""),
            prenom=self.validated_data.get("prenom", ""),
            contact=self.validated_data.get("contact", ""),
            civilite=self.validated_data.get("civilite", ""),
            role=self.validated_data.get("role", ""),
            fonction=self.validated_data.get("fonction", ""),
            company=self.validated_data.get("company", ""),
            sector=self.validated_data.get("sector", ""),
            description=self.validated_data.get("description", ""),
            is_active=False  # L'email doit être validé avant activation
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour le modèle Profile """

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_nom = serializers.CharField(source="user.nom", read_only=True)
    user_prenom = serializers.CharField(source="user.prenom", read_only=True)
    user_role = serializers.CharField(source="user.get_role_display", read_only=True)

    photo = serializers.SerializerMethodField()
    miniature = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "user_email", "user_nom", "user_prenom", "user_role",
            "photo", "miniature", "badge", "linkedin", "twitter",
            "website", "address", "birth_date", "bio"
        ]

    def get_photo(self, obj):
        return self.get_secure_url(obj.photo)

    def get_miniature(self, obj):
        return self.get_secure_url(obj.miniature)

    def get_badge(self, obj):
        return self.get_secure_url(obj.badge)

    def get_user_role(self, obj):
        """ Récupère le rôle de l'utilisateur avec une valeur par défaut si nécessaire """
        if obj.user.role:
            return obj.user.get_role_display()
        return "Non défini"  # ✅ Correction : Empêche la valeur `null`

    def get_secure_url(self, image_field):
        """ Génère une URL HTTPS complète pour une image si elle existe """
        request = self.context.get("request")
        if image_field:
            url = request.build_absolute_uri(image_field.url) if request else f"{settings.MEDIA_URL}{image_field.name}"
            return url.replace("http://", "https://")  # 🔒 Force HTTPS
        return None


class UserSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour l'utilisateur et son profil """
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["civilite", "nom", "prenom", "email", "contact", "role", "fonction", "company", "sector",
                  "description", "preferences", "profile"]

    def update(self, instance, validated_data):
        """ Mise à jour de l'utilisateur et du profil """
        profile_data = validated_data.pop("profile", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class CustomLoginSerializer(LoginSerializer):
    """ Sérialiseur personnalisé pour la connexion (sans username) """
    username = None
    email = serializers.EmailField()


class BeToBeSerializer(serializers.ModelSerializer):
    sponsor_name = serializers.CharField(source='sponsor.nom', read_only=True)

    class Meta:
        model = BeToBe
        fields = ["id", "sponsor", "sponsor_name", "date", "start_time", "end_time", "details"]


class MeetingSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(source='participant.nom', read_only=True)

    class Meta:
        model = Meeting
        fields = ["id", "btob", "participant", "participant_name", "confirmed_at"]


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source="organizer.nom", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "description", "start_date", "end_date", "location", "organizer", "organizer_name"]


class SpeakerSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour renvoyer toutes les informations du speaker """
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "civilite", "nom", "prenom", "fonction", "company", "photo", "sector",
                  "description"]

    def get_photo(self, obj):
        """ Récupérer l'URL de la photo du speaker à partir de son profil """
        if hasattr(obj, "profile") and obj.profile.photo:
            return obj.profile.photo.url  # Retourne l'URL de l'image
        return None  # Si pas de photo, retourner None


class SessionSerializer(serializers.ModelSerializer):
    """ Sérialiseur des sessions avec les détails du speaker """
    qr_code_url = serializers.SerializerMethodField()
    speaker = SpeakerSerializer(read_only=True)  # Renvoie toutes les infos du speaker

    class Meta:
        model = Session
        fields = ["id", "uuid", "event", "speaker", "title", "description", "start_time", "end_time", "qr_code_url",
                  "slug"]

    def get_qr_code_url(self, obj):
        if obj.qr_code:
            return obj.qr_code.url
        return None

    def create(self, validated_data):
        """ Générer un UUID et un QR Code lors de la création """
        session = Session(**validated_data)

        # Générer un UUID unique
        session.uuid = str(uuid.uuid4().int)[:8]
        session.slug = slugify(f"{session.title}-{session.uuid}")

        # Générer un QR Code basé sur le slug
        current_site = Site.objects.get_current()
        qr_data = f"https://{current_site.domain}{reverse('scan-qr', kwargs={'slug': session.slug})}"

        qr = qrcode.make(qr_data)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')

        # Sauvegarde du QR Code
        session.qr_code.save(f"qr_{session.slug}.png", File(qr_io), save=False)
        session.save()
        return session


class AttendanceSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source="session.title", read_only=True)
    user_name = serializers.CharField(source="user.nom", read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "user", "session", "session_title", "user_name", "scanned_at"]


class TemoignageSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(source="participant.nom", read_only=True)

    class Meta:
        model = Temoignage
        fields = ["id", "participant", "participant_name", "nom", "email", "telephone", "temoignage", "note", "statut",
                  "date_soumission", "date_validation"]


# class MeetingSerializer(serializers.ModelSerializer):
#     participant_name = serializers.CharField(source="participant.nom", read_only=True)
#     sponsor_name = serializers.CharField(source="btob.sponsor.nom", read_only=True)
#
#     class Meta:
#         model = Meeting
#         fields = ["id", "btob", "participant", "participant_name", "sponsor_name", "confirmed_at"]
#
#
# class AlbumSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Album
#         fields = "__all__"
#
#
# class PhotoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Photo
#         fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class BlogPostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.CharField(source="author.nom", read_only=True)

    class Meta:
        model = BlogPost
        fields = ["id", "title", "slug", "category", "category_name", "author", "author_name", "content", "image",
                  "created_at", "updated_at", "published_at", "status"]


class CommentSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "post_title", "author", "email", "content", "created_at", "approved"]


class GuestarsSpeakerSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour afficher les détails du Guestars Speaker, y compris la photo """
    nom = serializers.CharField(source="user.nom", read_only=True)
    prenom = serializers.CharField(source="user.prenom", read_only=True)
    photo = serializers.SerializerMethodField()  # Correction de l'accès à la photo

    class Meta:
        model = GuestarsSpeaker
        fields = ["id", "photo", "nom", "prenom", "fonction", "organisme", "bio"]

    def get_photo(self, obj):
        """ Récupérer l'URL de la photo du speaker à partir de son profil """
        if hasattr(obj.user, "profile") and obj.user.profile.photo:
            return obj.user.profile.photo.url  # Retourne l'URL de l'image
        return None  # Si pas de photo, retourne None
