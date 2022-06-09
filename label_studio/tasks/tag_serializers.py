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
from rest_framework.serializers import ALL_FIELDS
from tasks.models import TaskDbTag
from projects.models import Project


class TagCreatedSerializer(ModelSerializer):
    """
    """
    class Meta:
        model = TaskDbTag
        fields = ALL_FIELDS


class TagUpdatedSerializer(TagCreatedSerializer):
    pass


class TagListSerializer(ModelSerializer):
    pass

    class Meta:
        model = TaskDbTag
        fields = ALL_FIELDS


class TagDetailSerializer(TagListSerializer):
    pass
