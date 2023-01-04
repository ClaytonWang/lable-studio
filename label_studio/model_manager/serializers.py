"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
from django.conf import settings
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from projects.serializers_set import ProjectSetDetailSerializer
from model_manager.models import ModelManager
from model_manager.models import MODEL_TYPE


class ModelManagerListSerializer(serializers.ModelSerializer):
    """
    模型导入名称，对应数据表的模型集
    实际模型名字通过【模型集】+ 【版本输出】
    """
    url = SerializerMethodField()
    title_version = SerializerMethodField()
    created_by = UserSimpleSerializer(default={}, help_text='created owner')
    project = SerializerMethodField()
    model_type = SerializerMethodField()
    model_parameter = SerializerMethodField()
    # project_set = ProjectSetDetailSerializer(default={})

    @staticmethod
    def get_model_parameter(obj):
        if obj.model_parameter:
            try:
                return json.loads(obj.model_parameter)
            except Exception as e:
                print(e)
                return obj.model_parameter
        else:
            return None

    @staticmethod
    def get_url(obj):
        return settings.MODEL_SERVING_HOST

    @staticmethod
    def get_project(obj):
        return obj.project.title if obj.project else None

    @staticmethod
    def get_model_type(obj):
        return dict(MODEL_TYPE).get(obj.model_type, '')

    @staticmethod
    def get_title_version(obj):
        tv = obj.title + obj.version
        return tv + ' ' + obj.project.title if obj.project else tv

    class Meta:
        model = ModelManager
        ordering = ['-created_at']
        exclude = ['is_delete']
        # fields = '__all__'


class ModelManagerDetailSerializer(ModelManagerListSerializer):
    class Meta:
        model = ModelManager
        fields = '__all__'


class ModelManagerCreateSerializer(serializers.ModelSerializer):

    """
    """
    created_by_id = serializers.IntegerField(required=True)
    organization_id = serializers.IntegerField(required=True)

    class Meta:
        model = ModelManager
        fields = (
            'title', 'model', 'organization_id', 'created_by_id',
            'version', 'project', 'url', 'type', 'model_parameter',
        )


class ModelManagerUpdateSerializer(ModelManagerCreateSerializer):

    """
    """
    created_by_id = serializers.IntegerField(required=False)
    organization_id = serializers.IntegerField(required=False)


# def validate_label_config(self, config):
#     Project.validate_label_config(config)
#     return config


class ModelManagerSubDetailSerializer(ModelManagerListSerializer):
    text = SerializerMethodField()

    @staticmethod
    def get_text(obj):
        return f'{obj.title}{obj.version}'

    class Meta:
        model = ModelManager
        fields = ['id', 'title', 'version', 'text', 'type']
