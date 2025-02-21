from dj_rest_auth.registration.views import RegisterView
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from administration.api.serializers import BeToBeSerializer, MeetingSerializer, CustomRegisterSerializer, \
    UserSerializer, AlbumSerializer, PhotoSerializer, CategorySerializer, BlogPostSerializer, CommentSerializer, \
    GuestarsSpeakerSerializer
from public.models import BeToBe, Meeting, Album, Photo, Category, BlogPost, Comment, GuestarsSpeaker


class CustomRegisterView(RegisterView):
    """ Vue d'inscription personnalisée """
    serializer_class = CustomRegisterSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """ Vue pour récupérer et mettre à jour le profil utilisateur """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """ Vue pour changer le mot de passe """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Ancien mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Mot de passe mis à jour avec succès"}, status=status.HTTP_200_OK)


class BeToBeViewSet(viewsets.ModelViewSet):
    queryset = BeToBe.objects.all()
    serializer_class = BeToBeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """ Surcharge la méthode `list` pour s'assurer que la réponse est un tableau """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # 🔍 S'assure que la réponse est bien une liste `[]`


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """ Surcharge la méthode `list` pour s'assurer que la réponse est un tableau """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  # 🔍 S'assure que la réponse est bien une liste `[]`


class MeetingViewSet(viewsets.ModelViewSet):
    """ Gestion des rendez-vous entre participants et sponsors """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)


class AlbumViewSet(viewsets.ModelViewSet):
    """ Gestion des albums photos """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]


class PhotoViewSet(viewsets.ModelViewSet):
    """ Gestion des photos dans les albums """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    """ Gestion des catégories d'articles """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Tout le monde peut voir les catégories


class BlogPostViewSet(viewsets.ModelViewSet):
    """ Gestion des articles de blog """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ Gestion des commentaires sur les articles """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]  # Les commentaires peuvent être créés sans authentification


class GuestarsSpeakerViewSet(viewsets.ModelViewSet):
    """ Gestion des intervenants """
    queryset = GuestarsSpeaker.objects.all()
    serializer_class = GuestarsSpeakerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)