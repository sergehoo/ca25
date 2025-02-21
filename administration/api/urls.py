from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import BeToBeViewSet, MeetingViewSet, CustomRegisterView, UserProfileView, ChangePasswordView, AlbumViewSet, \
    PhotoViewSet, CategoryViewSet, BlogPostViewSet, CommentViewSet, GuestarsSpeakerViewSet

router = DefaultRouter()
router.register(r'btob', BeToBeViewSet)
# router.register(r'meetings', MeetingViewSet)

router.register(r"meetings", MeetingViewSet, basename="meeting")
router.register(r"albums", AlbumViewSet, basename="album")
router.register(r"photos", PhotoViewSet, basename="photo")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"blogposts", BlogPostViewSet, basename="blogpost")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"guestarspeakers", GuestarsSpeakerViewSet, basename="guestarspeaker")

urlpatterns = [
    path("organisateur/", include(router.urls)),

    path("auth/register/", CustomRegisterView.as_view(), name="register"),
    # path("auth/login/", LoginView.as_view(), name="login"),
    # path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/profile/", UserProfileView.as_view(), name="profile"),
    path("auth/profile/update/", UserProfileView.as_view(), name="profile-update"),
    # path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),

    path("auth/", include("dj_rest_auth.urls")),  # Connexion, Déconnexion, Changement de mot de passe
    path("auth/registration/", include("dj_rest_auth.registration.urls")),  # Inscription
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Rafraîchir le token JWT

]
