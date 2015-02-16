# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from rest_framework import serializers

from samples.utils import SampleHelper


class UserSerializer(serializers.ModelSerializer):

    """
    Serializer for model 'User'
    """

    class Meta:
        model = User
        fields = ('username',)


class SampleUploadSerializer(serializers.Serializer):

    """
    Serializer for uploading samples.
    """

    sample = serializers.FileField()

    def create(self, validated_data):
        """
        This method serves uploading samples.
        """
        sample_fp = validated_data.get('sample', None)
        user = validated_data.get('user', None)
        helper = SampleHelper(sample_fp)
        sample = helper.save(user=user)
        return sample

    def update(self, instance, validated_data):
        user = validated_data.get('user')
        sample_fp = validated_data.get('sample', None)
        helper = SampleHelper(sample_fp)
        sample = helper.save(user=user)
        return sample

    def to_representation(self, instance):
        ret = {}
        ret['sha256'] = instance.sha256
        return ret
