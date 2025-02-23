# Generated by Django 4.2.18 on 2025-02-23 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scanned_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('location', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=8, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('qr_code', models.ImageField(blank=True, upload_to='qr_codes/')),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
            ],
        ),
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
            ],
            options={
                'verbose_name': 'Témoignage',
                'verbose_name_plural': 'Témoignages',
                'ordering': ['-date_soumission'],
            },
        ),
    ]
