import uuid
from io import BytesIO

import qrcode
from django.contrib.sites.models import Site
from django.core.files import File
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer

from administration.models import Event, Session, Attendance, Temoignage
from public.models import BeToBe, Meeting, Photo, Album, User, Profile, Category, BlogPost, Comment, GuestarsSpeaker


class CustomRegisterSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour l'inscription de l'utilisateur """
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["civilite", "nom", "prenom", "email", "contact", "role", "password1", "password2"]

    def validate(self, data):
        """ Vérification des mots de passe """
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        """ Création de l'utilisateur """
        password = validated_data.pop("password1")
        validated_data.pop("password2")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)  # Créer un profil vide par défaut
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour le profil utilisateur """
    class Meta:
        model = Profile
        fields = ["photo", "miniature", "linkedin", "twitter", "website", "address", "birth_date", "bio"]


class UserSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour l'utilisateur et son profil """
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["civilite", "nom", "prenom", "email", "contact", "role", "fonction", "company", "sector", "description", "preferences", "profile"]

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


class SessionSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ["id", "uuid", "event", "speaker", "title", "description", "start_time", "end_time", "qr_code_url", "slug"]

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
        fields = ["id", "participant", "participant_name", "nom", "email", "telephone", "temoignage", "note", "statut", "date_soumission", "date_validation"]

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
        fields = ["id", "title", "slug", "category", "category_name", "author", "author_name", "content", "image", "created_at", "updated_at", "published_at", "status"]


class CommentSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "post_title", "author", "email", "content", "created_at", "approved"]


class GuestarsSpeakerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.nom", read_only=True)

    class Meta:
        model = GuestarsSpeaker
        fields = ["id", "user", "user_name", "fonction", "organisme", "facebook", "linkedin", "twitter", "website", "address", "birth_date", "bio"]