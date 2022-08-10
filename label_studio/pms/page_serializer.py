#!/usr/bin/env python
# encoding: utf-8

"""
  > FileName: serializer.py
  > Author: Yin
  > Mail: jindu.yin@digitalbrain.cn
  > CreatedTime: 2022/04/17 17:05
"""

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import CharField
from .models import PmsPage


"""
菜单权限
"""


class PmsPageCreatedSerializer(ModelSerializer):
    """
    """
    class Meta:
        model = PmsPage
        fields = '__all__'


class PmsPageUpdatedSerializer(PmsPageCreatedSerializer):
    code = CharField(required=False)
    title = CharField(required=False)
    pass


class PmsPageListSerializer(ModelSerializer):

    count = SerializerMethodField()

    @staticmethod
    def get_count(obj):
        return obj.group.count() + obj.user.count()

    class Meta:
        model = PmsPage
        fields = '__all__'


class PmsPageDetailSerializer(PmsPageListSerializer):
    pass

