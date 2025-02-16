# Generated by Django 4.2.18 on 2025-02-16 17:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administration', '0003_session_speaker'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temoignage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255, verbose_name='Nom du participant')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('telephone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Téléphone')),
                ('temoignage', models.TextField(verbose_name='Témoignage')),
                ('note', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5, verbose_name='Note')),
                ('statut', models.CharField(choices=[('En attente', 'En attente'), ('Validé', 'Validé'), ('Rejeté', 'Rejeté')], default='En attente', max_length=20, verbose_name='Statut')),
                ('date_soumission', models.DateTimeField(auto_now_add=True, verbose_name='Date de soumission')),
                ('date_validation', models.DateTimeField(blank=True, null=True, verbose_name='Date de validation')),
                ('participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='temoignages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Témoignage',
                'verbose_name_plural': 'Témoignages',
                'ordering': ['-date_soumission'],
            },
        ),
    ]
