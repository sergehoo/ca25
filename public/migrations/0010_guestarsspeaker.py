# Generated by Django 4.2.18 on 2025-02-17 09:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0009_blogpost_category_comment_blogpost_category'),
    ]

    operations = [
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
    ]
