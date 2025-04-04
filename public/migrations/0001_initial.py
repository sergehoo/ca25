# Generated by Django 4.2.18 on 2025-03-01 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import public.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('civilite', models.CharField(blank=True, choices=[('Monsieur', 'Monsieur'), ('Madame', 'Madame'), ('Docteur', 'Docteur'), ('Professeur', 'Professeur'), ('Pasteur', 'Pasteur'), ('Bishop', 'Bishop'), ('Excellence', 'Excellence'), ('Honorable', 'Honorable')], max_length=10, null=True)),
                ('nom', models.CharField(blank=True, max_length=50, null=True)),
                ('prenom', models.CharField(blank=True, max_length=100, null=True)),
                ('contact', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Adresse email')),
                ('role', models.CharField(blank=True, choices=[('participant', 'Participant'), ('exposant', 'Exposant'), ('orateur', 'Orateur'), ('fiss', 'FISS'), ('sponsor', 'Sponsor'), ('media', 'Media'), ('organisateur', 'Organisateur')], max_length=20, null=True)),
                ('fonction', models.CharField(blank=True, max_length=255, null=True)),
                ('company', models.CharField(blank=True, max_length=255, null=True)),
                ('sector', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('preferences', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Utilisateur',
                'verbose_name_plural': 'Utilisateurs',
                'ordering': ['nom', 'prenom'],
            },
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BeToBe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('details', models.CharField(blank=True, max_length=255, null=True)),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='btb_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('published', 'Publié')], default='draft', max_length=10)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='VisitCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('isp', models.CharField(blank=True, max_length=255, null=True)),
                ('is_mobile', models.BooleanField(default=False)),
                ('is_tablet', models.BooleanField(default=False)),
                ('is_pc', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('miniature', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('badge', models.ImageField(blank=True, null=True, upload_to='badges/')),
                ('linkedin', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=public.models.album_upload_path)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('date_ajout', models.DateTimeField(auto_now_add=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='public.album')),
            ],
        ),
        migrations.CreateModel(
            name='GuestarsSpeaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fonction', models.CharField(blank=True, max_length=255, null=True)),
                ('organisme', models.CharField(blank=True, max_length=255, null=True)),
                ('facebook', models.URLField(blank=True, null=True)),
                ('linkedin', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='guestartspeaker', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='public.blogpost')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='public.category'),
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed_at', models.DateTimeField(auto_now_add=True)),
                ('btob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='public.betobe')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant_meetings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('participant', 'btob')},
            },
        ),
    ]
