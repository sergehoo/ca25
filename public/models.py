import os
import uuid
from datetime import datetime
from io import BytesIO

import cv2
import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.utils.text import slugify
from django.utils.timezone import now, make_aware


# Create your models here.
class User(AbstractUser):
    ROLES = [
        ('participant', 'Participant'),
        ('exposant', 'Exposant'),
        ('sponsor', 'Sponsor'),
        ('media', 'Media'),
        ('organisateur', 'Organisateur'),
    ]
    CIVILITE_CHOICES = [
        ('Monsieur', 'Monsieur'),
        ('Madame', 'Madame'),
        ('Docteur', 'Docteur'),
        ('Professeur', 'Professeur'),
        ('Pasteur', 'Pasteur'),
        ('Bishop', 'Bishop'),
        ('Excellence', 'Excellence'),
        ('Honorable', 'Honorable'),
    ]
    civilite = models.CharField(max_length=10, choices=CIVILITE_CHOICES, blank=True, null=True)
    nom = models.CharField(max_length=50, blank=True, null=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    role = models.CharField(max_length=20, choices=ROLES, blank=True, null=True)
    fonction = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)  # Secteur d'activité
    description = models.TextField(blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)  # Régimes alimentaires ou autres

    # Ajoutez des `related_name` uniques ici pour éviter les conflits
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    USERNAME_FIELD = "email"  # Utilisation de l'email comme identifiant
    REQUIRED_FIELDS = ["nom", "prenom"]

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.email})"

    class Meta:
        ordering = ["nom", "prenom"]
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


class Profile(models.Model):
    """ Profil utilisateur avec gestion avancée des images (WebP & Miniature) """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    miniature = models.ImageField(upload_to="profiles/", blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """ Sauvegarde et conversion en WebP """
        super().save(*args, **kwargs)
        if self.photo:
            self.force_webp_conversion()
            self.generate_miniature()
            super().save(update_fields=["photo"])

    def force_webp_conversion(self):
        """ Convertit n'importe quel format en WebP avec compression optimisée """
        if not self.photo:
            return

        image_path = self.photo.path
        target_size = (900, 1333)  # Taille standardisée
        output_format = "webp"  # AVIF possible si Pillow le supporte

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")  # WebP ne supporte pas CMYK ou GIF

                # Vérifier si WebP est supporté
                from PIL import features
                if not features.check("webp"):
                    print("⚠️ WebP n'est pas supporté par cette version de Pillow !")
                    return

                # Recadrage intelligent pour conserver la proportion
                img_ratio = img.width / img.height
                target_ratio = target_size[0] / target_size[1]

                if img_ratio > target_ratio:
                    new_width = int(target_ratio * img.height)
                    left = (img.width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, img.height))
                else:
                    new_height = int(img.width / target_ratio)
                    top = (img.height - new_height) // 4
                    img = img.crop((0, top, img.width, top + new_height))

                # Redimensionnement final
                img = img.resize(target_size, Image.LANCZOS)

                # Convertir en WebP
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=85)

                # Renommer et sauvegarder en WebP
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                new_filename = f"profiles/{base_name}.webp"

                self.photo.save(new_filename, ContentFile(buffer.getvalue()), save=False)

                # Supprimer l'ancien fichier s'il existe
                if os.path.exists(image_path):
                    os.remove(image_path)

        except Exception as e:
            print(f"❌ Erreur lors de la conversion en WebP : {e}")

    def generate_miniature(self):
        """ Génère une miniature WebP centrée sur le visage """
        if not self.photo:
            return

        image_path = self.photo.path
        output_size = (600, 600)  # Taille standardisée

        try:
            img = cv2.imread(image_path)
            if img is None:
                return

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                x, y, w, h = faces[0]

                margin_x = int(w * 0.8)
                margin_y = int(h * 0.8)

                x1 = max(0, x - margin_x)
                y1 = max(0, y - margin_y)
                x2 = min(img.shape[1], x + w + margin_x)
                y2 = min(img.shape[0], y + h + margin_y)

                img_cropped = img[y1:y2, x1:x2]
            else:
                img_cropped = img

            # Rogner proprement pour 600x600
            crop_x, crop_y = img_cropped.shape[1], img_cropped.shape[0]
            target_ratio = output_size[0] / output_size[1]
            img_ratio = crop_x / crop_y

            if img_ratio > target_ratio:
                new_width = int(target_ratio * crop_y)
                left = (crop_x - new_width) // 2
                img_cropped = img_cropped[:, left:left + new_width]
            else:
                new_height = int(crop_x / target_ratio)
                top = (crop_y - new_height) // 2
                img_cropped = img_cropped[top:top + new_height, :]

            img_resized = cv2.resize(img_cropped, output_size, interpolation=cv2.INTER_AREA)

            # Convertir en WebP
            is_success, buffer = cv2.imencode(".webp", img_resized)
            if is_success:
                file_buffer = BytesIO(buffer)
                self.miniature.save(f"miniature_{self.user.id}.webp", ContentFile(file_buffer.getvalue()), save=False)

            super().save(update_fields=["miniature"])

        except Exception as e:
            print(f"❌ Erreur lors du traitement de la miniature : {e}")

    def __str__(self):
        return f"Profil de {self.user.nom} {self.user.prenom}"


class BeToBe(models.Model):
    """ Représente une session de rendez-vous organisée par un sponsor """
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="btb_sessions")  # Le sponsor qui organise la session
    date = models.DateField()  # Date de la rencontre
    start_time = models.TimeField()  # Heure de début
    end_time = models.TimeField()  # Heure de fin
    details = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["date", "start_time"]

    def clean(self):
        """ Validation des horaires """
        if self.start_time >= self.end_time:
            raise ValidationError("L'heure de début doit être avant l'heure de fin.")

    @property
    def is_expired(self):
        """ Vérifie si la session est expirée en fonction de la date et de l'heure actuelle """
        now_time = now()  # Datetime aware (avec timezone)

        # Créer un datetime "aware" basé sur la date et l'heure de fin de la session
        session_datetime = datetime.combine(self.date, self.end_time)

        if now_time.tzinfo is not None:  # Si now() a une timezone, applique-la aussi
            session_datetime = make_aware(session_datetime, now_time.tzinfo)

        return now_time > session_datetime  # Compare deux datetimes "aware"

    @property
    def meeting_count(self):
        """ Retourne le nombre de meetings créés pour cette session """
        return self.meetings.count()

    def __str__(self):
        return f"Session B2B avec {self.sponsor.nom} le {self.date.strftime('%d/%m/%Y')} de {self.start_time.strftime('%H:%M')} à {self.end_time.strftime('%H:%M')}"


class Meeting(models.Model):
    """ Représente un rendez-vous entre un participant et un sponsor """
    btob = models.ForeignKey(BeToBe, on_delete=models.CASCADE, related_name="meetings")
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participant_meetings"
    )
    confirmed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("participant", "btob")

    def clean(self):
        """ Vérifie les contraintes avant d'enregistrer un meeting """
        # Vérifier que le participant ne dépasse pas 5 rendez-vous
        if Meeting.objects.filter(participant=self.participant).count() >= 5:
            raise ValidationError("Vous ne pouvez pas avoir plus de 5 rendez-vous avec des sponsors.")

        # Vérifier que l'utilisateur sponsorise bien cet événement
        if self.btob.sponsor.role != "sponsor":
            raise ValidationError("L'utilisateur associé à cette session B2B n'est pas un sponsor.")

        # Vérifier si le créneau est déjà pris pour ce participant avec ce sponsor
        conflicts = Meeting.objects.filter(
            participant=self.participant,
            btob__sponsor=self.btob.sponsor
        ).exists()

        if conflicts:
            raise ValidationError("Vous avez déjà un rendez-vous avec ce sponsor.")

    def save(self, *args, **kwargs):
        """ Valide et sauvegarde la rencontre """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.participant.nom} rencontre {self.btob.sponsor.nom} le {self.btob.date.strftime('%d/%m/%Y')} à {self.btob.start_time.strftime('%H:%M')}"


class Album(models.Model):
    titre = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


def album_upload_path(instance, filename):
    """ Génère un chemin de stockage en fonction du nom de l'album """
    album_slug = slugify(instance.album.titre)  # Convertit le titre en slug
    filename_base, file_extension = os.path.splitext(filename)
    return f"gallery/{album_slug}/{filename_base}{file_extension}"


class Photo(models.Model):
    album = models.ForeignKey(Album, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=album_upload_path)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """ Génère l'URL complète de l'image pour le partage """
        if self.image:
            return f"{settings.MEDIA_URL}{self.image.name}"
        return ""

    def get_share_links(self):
        """ Génère les liens de partage pour Facebook, Twitter, WhatsApp, LinkedIn """
        url = f"{settings.SITE_URL}{self.get_absolute_url()}"

        return {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={url}",
            "twitter": f"https://twitter.com/intent/tweet?url={url}&text=Regardez cette photo !",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={url}",
            "whatsapp": f"https://api.whatsapp.com/send?text=Regardez cette photo ! {url}"
        }

    def save(self, *args, **kwargs):
        """ Sauvegarde et conversion automatique en WebP """
        super().save(*args, **kwargs)
        if self.image:
            self.convert_to_webp()
            super().save(update_fields=["image"])

    def convert_to_webp(self):
        """ Convertit l'image en WebP quel que soit le format d'origine """
        if not self.image:
            return

        image_path = self.image.path
        output_format = "webp"  # Format cible
        target_size = (1200, 800)  # Taille standardisée pour uniformiser les images

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")  # WebP ne supporte pas CMYK

                # Vérification du support WebP
                from PIL import features
                if not features.check("webp"):
                    print("⚠️ WebP non supporté par Pillow, conversion annulée.")
                    return

                # Redimensionnement proportionnel
                img.thumbnail(target_size, Image.LANCZOS)

                # Compression et sauvegarde en WebP
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=90)

                # Générer un nouveau nom de fichier
                # base_name = os.path.splitext(os.path.basename(image_path))[0]
                # new_filename = f"{base_name}.webp"

                # album_slug = slugify(self.album.titre)
                unique_id = uuid.uuid4().hex[:8]  # Génère un ID unique (8 caractères)
                new_filename = f"{unique_id}.webp"

                self.image.save(new_filename, ContentFile(buffer.getvalue()), save=False)

                # Supprimer l'ancien fichier s'il existe encore
                if os.path.exists(image_path):
                    os.remove(image_path)

        except Exception as e:
            print(f"❌ Erreur lors de la conversion en WebP : {e}")

    def __str__(self):
        return f"Photo de {self.album.titre}"

    def __str__(self):
        return f"Photo de {self.album.titre}"


class Category(models.Model):
    """ Catégorie d'article """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """ Modèle principal des articles de blog """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié')
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    content = models.TextField()
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """ Modèle des commentaires sur les articles """
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    author = models.CharField(max_length=255)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.author} sur {self.post.title}"


class GuestarsSpeaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="guestartspeaker")
    fonction = models.CharField(max_length=255, blank=True, null=True)
    organisme = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f" {self.user} sur {self.fonction}"


class VisitCounter(models.Model):
    ip_address = models.GenericIPAddressField()  # Adresse IP du visiteur
    user_agent = models.TextField(blank=True, null=True)  # Infos sur le navigateur
    timestamp = models.DateTimeField(default=now)  # Date et heure de la visite
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Utilisateur (si connecté)

    # Localisation
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    isp = models.CharField(max_length=255, blank=True, null=True)  # Fournisseur d'accès Internet

    # Type d'appareil
    is_mobile = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_pc = models.BooleanField(default=False)

    def __str__(self):
        device = "Mobile" if self.is_mobile else "Tablette" if self.is_tablet else "PC"
        return f"Visite de {self.ip_address} ({device}, {self.city}, {self.country}) - {self.timestamp}"

    @staticmethod
    def get_location(ip):
        """Utilise une API externe pour récupérer la localisation de l'IP."""
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}")
            data = response.json()
            if data['status'] == 'success':
                return {
                    "country": data.get("country"),
                    "city": data.get("city"),
                    "region": data.get("regionName"),
                    "postal_code": data.get("zip"),
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon"),
                    "isp": data.get("isp"),
                }
        except requests.RequestException:
            pass
        return {}

    def save(self, *args, **kwargs):
        """Remplit les informations de localisation et le type d'appareil avant de sauvegarder."""
        if not self.country and self.ip_address:
            location_data = self.get_location(self.ip_address)
            self.country = location_data.get("country")
            self.city = location_data.get("city")
            self.region = location_data.get("region")
            self.postal_code = location_data.get("postal_code")
            self.latitude = location_data.get("latitude")
            self.longitude = location_data.get("longitude")
            self.isp = location_data.get("isp")

        super().save(*args, **kwargs)
