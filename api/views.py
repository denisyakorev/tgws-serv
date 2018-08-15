from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from core.models import Publication, Module
from api.serializers import PublicationSerializer, ModuleSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def publication_detail(request, pubcode):
    data = {}
    try:
        publication = Publication.objects.get(code=pubcode)
        serializer = PublicationSerializer(publication)
        return Response(serializer.data)
    except Exception as err:
        data = {'error':err}

    return Response(data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def module_detail(request, module_id):
    data = {}
    try:
        module = Module.objects.get(pk=int(module_id))
        serializer = ModuleSerializer(module)
        return Response(serializer.data)
    except Exception:
        data = {'error': err}

    return Response(data, status=status.HTTP_400_BAD_REQUEST)