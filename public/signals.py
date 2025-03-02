from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from public.models import Profile


# Signal pour créer un profil automatiquement lors de la création d'un utilisateur

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Crée un profil automatiquement lorsqu'un utilisateur est créé """
    if created:
        print(f"🔔 Création d'un profil pour {instance.email}")  # Debug
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Sauvegarde automatiquement le profil lorsque l'utilisateur est mis à jour """
    instance.profile.save()


@receiver(user_signed_up)
def create_user_profile_on_signup(request, user, **kwargs):
    """ Crée un profil automatiquement lorsqu'un utilisateur s'inscrit via Django Allauth """
    Profile.objects.get_or_create(user=user)
    print(f"✅ Profil créé automatiquement pour {user.email}")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Création automatique d'un profil utilisateur si ce n'est pas fait via Allauth """
    if created:
        Profile.objects.get_or_create(user=instance)