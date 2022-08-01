#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName   : group_serializer.py.py
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > CreateTime : 2021/6/18 09:42
"""
from django.contrib.auth.models import Group, User
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField


class GroupCreatedSerializer(ModelSerializer):
    """
    """
    class Meta:
        model = Group
        fields = ('name', )


class GroupUpdatedSerializer(GroupCreatedSerializer):
    pass


class GroupListSerializer(ModelSerializer):
    count = SerializerMethodField()

    @staticmethod
    def get_count(obj):
        return obj.user_set.count()

    class Meta:
        model = Group
        fields = ('name', 'id', 'count')


class GroupDetailSerializer(GroupListSerializer):
    pass
