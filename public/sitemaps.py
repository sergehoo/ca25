from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from administration.models import Event
from public.models import GuestarsSpeaker


class StaticViewSitemap(Sitemap):
    """ Sitemap des pages statiques """
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ['home', 'about', 'programme', 'speakers', 'contact']

    def location(self, item):
        return reverse(item)


class EventSitemap(Sitemap):
    """ Sitemap des événements """
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Event.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Utilise la date de dernière modification


class SpeakerSitemap(Sitemap):
    """ Sitemap des intervenants """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return GuestarsSpeaker.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
