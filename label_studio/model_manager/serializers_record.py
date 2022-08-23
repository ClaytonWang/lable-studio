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
    created_by = UserSimpleSerializer(default={}, help_text='created owner')
    model_title_version = SerializerMethodField()
    new_model_title_version = SerializerMethodField()
    project_title = SerializerMethodField()
    project_set = SerializerMethodField()

    @staticmethod
    def get_project_set(obj):
        if obj.project and obj.project.set:
            return obj.project.set.title
        return ''

    @staticmethod
    def get_project_title(obj):
        return obj.project.title if obj.project else ''

    def get_new_model_title_version(self, obj):
        return self.model_version(obj.new_model)

    def get_model_title_version(self, obj):
        return self.model_version(obj.model)

    @staticmethod
    def model_version(model):
        return model.title + model.version if model else ''

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

