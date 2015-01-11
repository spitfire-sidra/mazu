# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    """
    Serializer for model 'User'
    """

    class Meta:
        model = User
        fields = ('username',)
