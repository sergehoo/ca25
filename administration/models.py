import uuid
from io import BytesIO

from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site

from django.core.files import File
from django.db import models
import qrcode
from django.utils.text import slugify
from django.shortcuts import reverse

from public.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")

    def __str__(self):
        return self.name


class Session(models.Model):
    uuid = models.CharField(max_length=8, unique=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sessions")
    speaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="speaker", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=255)

    #
    # def save(self, *args, **kwargs):
    #     qr = qrcode.make(f"session-{self.id}")
    #     qr_io = BytesIO()
    #     qr.save(qr_io, format='PNG')
    #     self.qr_code.save(f"qr_{self.id}.png", File(qr_io), save=False)
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Générer un UUID à 8 chiffres unique
        if not self.uuid:
            self.uuid = str(uuid.uuid4().int)[:8]

        # Générer un slug unique
        if not self.slug:
            self.slug = slugify(f"{self.event}-{self.title}-{self.uuid}")

        # URL de scan sécurisé
        current_site = Site.objects.get_current()
        scan_url = f"https://{current_site.domain}{reverse('scan-qr', kwargs={'slug': self.slug})}"

        # Générer le QR Code
        qr = qrcode.make(scan_url)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')

        # Sauvegarder le QR Code
        self.qr_code.save(f"qr_{self.slug}.png", File(qr_io), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="attendances")
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'session')  # Évite les doublons de participation

    def __str__(self):
        return f"{self.user} - {self.session.title}"


class Temoignage(models.Model):
    """
    Modèle pour recueillir les témoignages des participants à la Conférence d'Abidjan.
    """
    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('Validé', 'Validé'),
        ('Rejeté', 'Rejeté'),
    ]

    participant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="temoignages")
    nom = models.CharField(max_length=255, verbose_name=_("Nom du participant"))
    email = models.EmailField(verbose_name=_("Email"), blank=True, null=True)
    telephone = models.CharField(max_length=20, verbose_name=_("Téléphone"), blank=True, null=True)
    temoignage = models.TextField(verbose_name=_("Témoignage"))
    note = models.PositiveSmallIntegerField(verbose_name=_("Note"), choices=[(i, str(i)) for i in range(1, 6)],
                                            default=5)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En attente', verbose_name=_("Statut"))
    date_soumission = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de soumission"))
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de validation"))

    class Meta:
        ordering = ['-date_soumission']
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"

    def __str__(self):
        return f"{self.nom} - {self.temoignage[:50]}..."
