from allauth.account.adapter import DefaultAccountAdapter
from django.http import JsonResponse


class NoRedirectAccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        return JsonResponse({"error": "User account is inactive."}, status=400)

    def get_login_redirect_url(self, request):
        return None  # Désactive la redirection automatique


class NoUsernameAccountAdapter(DefaultAccountAdapter):
    def clean_username(self, username, strict=False):
        return ""  # Empêche l'utilisation d'un username
