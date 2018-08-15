from rest_framework import serializers
from core.models import Publication, Module

class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publication
        fields = ('title', 'code', 'structure_json')


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = ('id', 'tech_name', 'title', 'issue_number', 'content_json', 'is_category')