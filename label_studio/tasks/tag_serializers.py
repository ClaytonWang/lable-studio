#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : tag_serializers.py
  > CreateTime : 2022/6/7 12:42
"""
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import CharField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import Serializer
from rest_framework.serializers import ALL_FIELDS
from tasks.models import TaskDbAlgorithm
from projects.models import Project


class TagCleanCreatedSerializer(ModelSerializer):
    """
    """
    class Meta:
        model = TaskDbAlgorithm
        fields = ALL_FIELDS


class TagCleanUpdatedSerializer(TagCleanCreatedSerializer):
    project = Serializer(required=False)
    task = Serializer(required=False)
    pass


class TagCleanListSerializer(ModelSerializer):
    pass

    class Meta:
        model = TaskDbAlgorithm
        fields = ALL_FIELDS


class TagCleanDetailSerializer(TagCleanListSerializer):
    pass
