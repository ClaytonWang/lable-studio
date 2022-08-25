#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : serializers_train.py
  > CreateTime : 2022/8/3 09:07
"""
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from projects.serializers_set import ProjectSetDetailSerializer
from model_manager.models import ModelTrain


class ModelTrainListSerializer(serializers.ModelSerializer):
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
        model = ModelTrain
        fields = '__all__'


class ModelTrainDetailSerializer(ModelTrainListSerializer):
    class Meta:
        model = ModelTrain
        fields = '__all__'


class ModelTrainCreateSerializer(serializers.ModelSerializer):

    """
    """

    class Meta:
        model = ModelTrain
        fields = '__all__'


class ModelTrainUpdateSerializer(ModelTrainCreateSerializer):

    """
    """
    pass

