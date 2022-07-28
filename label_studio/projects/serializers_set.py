#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : serializers_set.py
  > CreateTime : 2022/7/25 14:56
"""
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from projects.models import ProjectSet
from users.serializers import UserSimpleSerializer


class ProjectSetListSerializer(serializers.ModelSerializer):
    """
    """
    created_by = UserSimpleSerializer(default={}, help_text='created owner')
    project_count = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_project_count(obj):
        return obj.project_set.count()

    class Meta:
        model = ProjectSet
        fields = '__all__'


class ProjectSetDetailSerializer(ProjectSetListSerializer):
    class Meta:
        model = ProjectSet
        fields = '__all__'


class ProjectSetCreateSerializer(serializers.ModelSerializer):

    """
    """
    created_by_id = serializers.IntegerField(required=True)
    updated_by_id = serializers.IntegerField(required=True)
    organization_id = serializers.IntegerField(required=True)

    class Meta:
        model = ProjectSet
        fields = ('title', 'organization_id', 'created_by_id', 'updated_by_id')


class ProjectSetUpdateSerializer(ProjectSetCreateSerializer):

    """
    """
    created_by_id = serializers.IntegerField(required=False)
    organization_id = serializers.IntegerField(required=False)
