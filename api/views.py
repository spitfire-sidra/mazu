# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from samples.models import Sample

from api.serializers import UserSerializer
from api.serializers import SampleUploadSerializer

"""
API endpoints
"""

class UserViewSet(viewsets.ViewSet):

    """
    A simple ViewSet that for listing or retrieving users.
    """

    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class SampleViewSet(viewsets.ViewSet):

    """
    A sample ViewSet that for uploading samples.
    """

    queryset = Sample.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        serializer = SampleUploadSerializer(request.data, request.FILES)
        if serializer.is_valid():
            serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
