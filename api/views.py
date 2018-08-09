from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response

from core.models import Publication, Module
from api.serializers import PublicationSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def publication_detail(request, pubcode):
    publication = Publication.objects.get(code=pubcode)
    serializer = PublicationSerializer(publication)
    return Response(serializer.data)
