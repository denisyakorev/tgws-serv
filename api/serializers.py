from rest_framework import serializers
from core.models import Publication, Module

class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publication
        fields = ('title', 'code', 'structure_json')