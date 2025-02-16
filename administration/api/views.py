from rest_framework import viewsets, permissions
from rest_framework.response import Response

from administration.api.serializers import BeToBeSerializer, MeetingSerializer
from public.models import BeToBe, Meeting


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
