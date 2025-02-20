from django.utils.timezone import now

import logging

from public.models import VisitCounter

logger = logging.getLogger(__name__)


class VisitCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Récupérer l'adresse IP du visiteur
        ip = self.get_client_ip(request)

        # Vérifier si l'IP a déjà été enregistrée aujourd'hui
        if not VisitCounter.objects.filter(ip_address=ip, timestamp__date=now().date()).exists():
            VisitCounter.objects.create(
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')  # Infos sur le navigateur
            )
            logger.info(f"Nouvelle visite enregistrée : {ip}")

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """ Récupérer l'IP réelle du visiteur en tenant compte des proxys. """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
