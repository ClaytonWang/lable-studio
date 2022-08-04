#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : serializers_record.py
  > CreateTime : 2022/8/3 09:07
"""
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from projects.serializers_set import ProjectSetDetailSerializer
from model_manager.models import ModelRecord


class ModelRecordListSerializer(serializers.ModelSerializer):
    """
    """

    title_version = SerializerMethodField()

    @staticmethod
    def get_title_version(obj):
        return obj.title + obj.version

    class Meta:
        model = ModelRecord
        fields = '__all__'


class ModelRecordDetailSerializer(ModelRecordListSerializer):
    class Meta:
        model = ModelRecord
        fields = '__all__'


class ModelRecordCreateSerializer(serializers.ModelSerializer):

    """
    """

    class Meta:
        model = ModelRecord
        fields = '__all__'


class ModelRecordUpdateSerializer(ModelRecordCreateSerializer):

    """
    """
    pass

