import uuid
from io import BytesIO

import qrcode
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.files.storage import default_storage
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
    """ Sérialiseur d'inscription personnalisé avec plusieurs champs """

    nom = serializers.CharField(required=True, max_length=50)
    prenom = serializers.CharField(required=True, max_length=100)
    civilite = serializers.ChoiceField(choices=User.CIVILITE_CHOICES, required=False, allow_null=True)
    sexe = serializers.ChoiceField(choices=User.sexe_CHOICES, required=False, allow_null=True)
    contact = serializers.CharField(required=False, allow_blank=True, max_length=100)
    role = serializers.ChoiceField(choices=User.ROLES, required=False, allow_null=True)
    fonction = serializers.CharField(required=False, allow_blank=True, max_length=255)
    company = serializers.CharField(required=False, allow_blank=True, max_length=255)
    pays = serializers.CharField(required=False, allow_blank=True, max_length=255)
    ville = serializers.CharField(required=False, allow_blank=True, max_length=255)
    sector = serializers.CharField(required=False, allow_blank=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.JSONField(required=False)

    def get_cleaned_data(self):
        """ Permet de récupérer les données avant enregistrement """
        data = super().get_cleaned_data()
        data.update({
            "nom": self.validated_data.get("nom", ""),
            "prenom": self.validated_data.get("prenom", ""),
            "civilite": self.validated_data.get("civilite", None),
            "sexe": self.validated_data.get("sexe", None),
            "contact": self.validated_data.get("contact", ""),
            "role": self.validated_data.get("role", None),
            "fonction": self.validated_data.get("fonction", ""),
            "company": self.validated_data.get("company", ""),
            "pays": self.validated_data.get("pays", ""),
            "ville": self.validated_data.get("ville", ""),
            "sector": self.validated_data.get("sector", ""),
            "description": self.validated_data.get("description", ""),
            "preferences": self.validated_data.get("preferences", {}),
        })
        return data

    def save(self, request):
        """ Sauvegarde les données personnalisées avec l'utilisateur """
        user = super().save(request)
        user.nom = self.validated_data.get("nom", "")
        user.prenom = self.validated_data.get("prenom", "")
        user.civilite = self.validated_data.get("civilite", None)
        user.sexe = self.validated_data.get("sexe", None)
        user.contact = self.validated_data.get("contact", "")
        user.role = self.validated_data.get("role", None)
        user.fonction = self.validated_data.get("fonction", "")
        user.company = self.validated_data.get("company", "")
        user.pays = self.validated_data.get("pays", "")
        user.ville = self.validated_data.get("ville", "")
        user.sector = self.validated_data.get("sector", "")
        user.description = self.validated_data.get("description", "")
        user.preferences = self.validated_data.get("preferences", {})
        cleaned_data = self.get_cleaned_data()
        user = User.objects.create_user(
            email=cleaned_data["email"],
            password=self.validated_data["password1"],
            **cleaned_data
        )

        user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "email", "password", "nom", "prenom", "civilite", "sexe",
            "contact", "role", "fonction", "company", "pays",
            "ville", "sector", "description", "preferences"
        ]

    def create(self, validated_data):
        """ ✅ Création de l'utilisateur avec un mot de passe hashé et un rôle par défaut """
        validated_data.setdefault("role", "participant")  # Définit "participant" si non fourni

        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Hash du mot de passe
        user.save()
        return user


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             "email", "nom", "prenom", "civilite", "sexe",
#             "contact", "role", "fonction", "company", "pays",
#             "ville", "sector", "description", "preferences"
#         ]
#
#     def create(self, validated_data):
#         """ ✅ Création de l'utilisateur sans mot de passe """
#         validated_data.setdefault("role", "participant")  # Définit "participant" si non fourni
#
#         user = User.objects.create(**validated_data)
#         return user


class UserProfileSerializer(serializers.ModelSerializer):
    """ Sérialiseur permettant la mise à jour des informations du profil ET de l'utilisateur """

    user_email = serializers.EmailField(source="user.email", read_only=True)  # Email inchangé
    user_id = serializers.CharField(source="user.id", required=False)
    user_nom = serializers.CharField(source="user.nom", required=False)
    user_prenom = serializers.CharField(source="user.prenom", required=False)
    user_sexe = serializers.CharField(source="user.sexe", required=False, allow_blank=True, allow_null=True)
    user_civilite = serializers.CharField(source="user.civilite", required=False, allow_blank=True, allow_null=True)
    user_contact = serializers.CharField(source="user.contact", required=False, allow_blank=True, allow_null=True)
    user_fonction = serializers.CharField(source="user.fonction", required=False, allow_blank=True, allow_null=True)
    user_company = serializers.CharField(source="user.company", required=False, allow_blank=True, allow_null=True)
    user_pays = serializers.CharField(source="user.pays", required=False, allow_blank=True, allow_null=True)
    user_ville = serializers.CharField(source="user.ville", required=False, allow_blank=True, allow_null=True)
    user_sector = serializers.CharField(source="user.sector", required=False, allow_blank=True, allow_null=True)
    user_description = serializers.CharField(source="user.description", required=False, allow_blank=True,
                                             allow_null=True)
    user_preferences = serializers.JSONField(source="user.preferences", required=False)

    user_role = serializers.SerializerMethodField()  # ✅ Corrige l'affichage des rôles

    # photo = serializers.ImageField(required=False, allow_null=True)
    # badge = serializers.ImageField(required=False, allow_null=True)
    # miniature = serializers.ImageField(required=False, allow_null=True)
    photo = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    miniature = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            # Champs de l'utilisateur
            "user_id", "user_email", "user_nom", "user_prenom", "user_sexe", "user_civilite",
            "user_contact", "user_fonction", "user_company", "user_pays", "user_ville",
            "user_sector", "user_description", "user_preferences", "user_role",
            # Champs du profil
            "photo", "badge", "miniature", "linkedin", "twitter",
            "website", "address", "birth_date", "bio"
        ]

    def get_user_role(self, obj):
        """ Récupère le rôle de l'utilisateur """
        return obj.user.get_role_display() if obj.user.role else "Non défini"

    def get_photo(self, obj):
        """ Génère l'URL HTTPS pour le champ `photo` """
        if obj.photo:
            return self._get_absolute_https_url(obj.photo)
        return None

    def get_badge(self, obj):
        """ Génère l'URL HTTPS pour le champ `badge` """
        if obj.badge:
            return self._get_absolute_https_url(obj.badge)
        return None

    def get_miniature(self, obj):
        """ Génère l'URL HTTPS pour le champ `miniature` """
        if obj.miniature:
            return self._get_absolute_https_url(obj.miniature)
        return None

    def _get_absolute_https_url(self, file_field):
        """
        Génère une URL absolue en HTTPS pour un champ de fichier.
        """
        if file_field:
            # Générer l'URL absolue en utilisant la requête
            request = self.context.get('request')
            if request:
                # Convertir le chemin relatif en URL absolue
                absolute_url = request.build_absolute_uri(file_field.url)
                # Forcer l'utilisation de HTTPS
                return absolute_url.replace("http://", "https://", 1)
        return None

    def update(self, instance, validated_data):
        """
        🔄 Mise à jour du profil ET de l'utilisateur en même temps.
        """
        user_data = validated_data.pop("user", {})  # Extraire les données utilisateur

        # ✅ Mise à jour des données de `User`
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()  # Sauvegarder les modifications de l'utilisateur

        # ✅ Mise à jour des données de `Profile`
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour l'utilisateur et son profil """
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["civilite", "id", "nom", "prenom", "email", "contact", "role", "fonction", "company", "sector",
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
