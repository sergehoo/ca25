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
    email = models.CharField(max_length=100, blank=True, null=True)
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


class Profile(models.Model):
    """ Profil utilisateur avec informations supplémentaires """
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
        """ Sauvegarde l'image après traitement """
        super().save(*args, **kwargs)
        if self.photo:
            self.process_image()
            self.process_miniature()

    def process_image(self):
        """ Rogner et redimensionner l’image sans la déformer """
        image_path = self.photo.path
        target_size = (900, 1333)  # Taille cible

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")  # Convertir en RGB si nécessaire

                # Calcul des proportions
                img_ratio = img.width / img.height
                target_ratio = target_size[0] / target_size[1]

                # Rognage intelligent pour conserver le visage centré
                if img_ratio > target_ratio:
                    # Image trop large -> Rogner sur la largeur
                    new_width = int(target_ratio * img.height)
                    left = (img.width - new_width) // 2
                    right = left + new_width
                    img = img.crop((left, 0, right, img.height))
                else:
                    # Image trop haute -> Rogner sur la hauteur
                    new_height = int(img.width / target_ratio)
                    top = (img.height - new_height) // 4  # Ajusté pour garder plus de place au-dessus du visage
                    bottom = top + new_height
                    img = img.crop((0, top, img.width, bottom))

                # Redimensionner à la taille exacte
                img = img.resize(target_size, Image.LANCZOS)

                # Sauvegarde optimisée
                img.save(image_path, quality=90)

        except Exception as e:
            print(f"Erreur lors du traitement de l'image : {e}")

    def process_miniature(self):
        """ Redimensionne et centre la miniature sans aplatir l’image """
        image_path = self.photo.path
        output_size = (600, 600)  # Taille cible de la miniature

        try:
            img = cv2.imread(image_path)  # Charger l'image avec OpenCV
            if img is None:
                return  # Évite les erreurs si l'image ne peut pas être chargée

            # Convertir en niveaux de gris pour la détection des visages
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Charger le modèle de détection de visages OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Détecter les visages
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            if len(faces) > 0:
                # Prendre le plus grand visage détecté (celui le plus proche de la caméra)
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)  # Trier par taille
                x, y, w, h = faces[0]

                # Définir une marge autour du visage
                margin_x = int(w * 0.8)  # Augmenter légèrement la zone autour du visage
                margin_y = int(h * 0.8)

                # Calculer les nouvelles dimensions de recadrage
                x1 = max(0, x - margin_x)
                y1 = max(0, y - margin_y)
                x2 = min(img.shape[1], x + w + margin_x)
                y2 = min(img.shape[0], y + h + margin_y)

                # Recadrer l'image autour du visage
                img_cropped = img[y1:y2, x1:x2]
            else:
                # Si aucun visage n'est détecté, rogner l'image pour garder le bon format
                img_cropped = img

            # Calcul des proportions pour rogner sans aplatir
            crop_x, crop_y = img_cropped.shape[1], img_cropped.shape[0]
            target_ratio = output_size[0] / output_size[1]
            img_ratio = crop_x / crop_y

            if img_ratio > target_ratio:
                # Image trop large : rogner sur la largeur
                new_width = int(target_ratio * crop_y)
                left = (crop_x - new_width) // 2
                img_cropped = img_cropped[:, left:left + new_width]
            else:
                # Image trop haute : rogner sur la hauteur
                new_height = int(crop_x / target_ratio)
                top = (crop_y - new_height) // 2
                img_cropped = img_cropped[top:top + new_height, :]

            # Redimensionner à la taille cible (600x600) sans déformation
            img_resized = cv2.resize(img_cropped, output_size, interpolation=cv2.INTER_AREA)

            # Sauvegarder la miniature en mémoire
            is_success, buffer = cv2.imencode(".jpg", img_resized)
            if is_success:
                file_buffer = BytesIO(buffer)
                self.miniature.save(f"miniature_{self.user.id}.jpg", ContentFile(file_buffer.getvalue()), save=False)

            # Sauvegarder le modèle avec la nouvelle miniature
            super().save(update_fields=["miniature"])

        except Exception as e:
            print(f"Erreur lors du traitement de l'image : {e}")

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


class Photo(models.Model):
    album = models.ForeignKey(Album, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="gallery/")
    description = models.CharField(max_length=255, blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

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
