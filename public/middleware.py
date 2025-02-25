from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

import logging

from django_user_agents.utils import get_user_agent

from public.models import VisitCounter

logger = logging.getLogger(__name__)


class VisitCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Détection du type d'appareil
        ua = get_user_agent(request)
        is_mobile = ua.is_mobile
        is_tablet = ua.is_tablet
        is_pc = ua.is_pc

        # Vérifie si l'utilisateur est connecté
        user = request.user if request.user.is_authenticated else None

        # Enregistre la visite
        VisitCounter.objects.create(
            ip_address=ip,
            user_agent=user_agent,
            user=user,
            is_mobile=is_mobile,
            is_tablet=is_tablet,
            is_pc=is_pc,
        )

    def get_client_ip(self, request):
        """Récupère l'adresse IP du visiteur."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class QRRedirectMiddleware:
    """ Redirige les scans QR vers l'application mobile ou le store """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/scan/"):
            slug = request.path.split("/")[-1]
            return HttpResponseRedirect(reverse("scan_redirect", kwargs={"slug": slug}))
        return self.get_response(request)


class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)