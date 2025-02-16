from rest_framework import serializers

from public.models import BeToBe, Meeting, Photo, Album


class BeToBeSerializer(serializers.ModelSerializer):
    sponsor_name = serializers.CharField(source='sponsor.nom', read_only=True)

    class Meta:
        model = BeToBe
        fields = ["id", "sponsor", "sponsor_name", "date", "start_time", "end_time", "details"]


class MeetingSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(source='participant.nom', read_only=True)

    class Meta:
        model = Meeting
        fields = ["id", "btob", "participant", "participant_name", "confirmed_at"]


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'