from rest_framework import serializers
from core.models import Publication, Module

class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publication
        fields = ('name', 'code', 'content_json')