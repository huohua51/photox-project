from rest_framework import serializers
from .models import Album
from images.serializers import ImageSerializer

class AlbumSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Album
        fields = ['id', 'title', 'description', 'user', 'images', 'is_public', 'created_at']
        read_only_fields = ['id', 'created_at']

class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['title', 'description', 'is_public']

class AlbumUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['title', 'description', 'is_public'] 