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
    new_model_train_task = SerializerMethodField()
    new_model_assessment_task = SerializerMethodField()

    @staticmethod
    def get_new_model_train_task(obj):
        return obj.train_task.count()

    @staticmethod
    def get_new_model_assessment_task(obj):
        return obj.assessment_task.count()

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
        exclude = ['train_task', 'assessment_task']
        # fields = '__all__'


class ModelTrainDetailSerializer(ModelTrainListSerializer):
    class Meta:
        model = ModelTrain
        fields = '__all__'


class ModelTrainCreateSerializer(serializers.ModelSerializer):

    """
    """
    model_id = serializers.IntegerField(required=True)
    new_model_id = serializers.IntegerField(required=False)
    project_id = serializers.IntegerField(required=True)
    created_by_id = serializers.IntegerField(required=True)
    updated_by_id = serializers.IntegerField(required=False)
    organization_id = serializers.IntegerField(required=False)

    class Meta:
        model = ModelTrain
        # fields = [item.name for item in ModelTrain._meta.local_fields] + [
        #     'model_id', 'new_model_id', 'project_id',
        #     'created_by_id', 'updated_by_id', 'organization_id'
        # ]
        fields = [
            'exactness_count', 'total_count', 'is_train',
            'accuracy_rate', 'new_accuracy_rate', 'training_progress', 'category', 'created_at',
            'updated_at', 'state', 'model_parameter', 'model_result', 'model_id', 'new_model_id',
            'project_id', 'created_by_id', 'updated_by_id', 'organization_id',
            'model_parameter']
        print('....')


class ModelTrainUpdateSerializer(ModelTrainCreateSerializer):

    """
    """
    pass

