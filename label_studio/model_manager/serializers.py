"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from model_manager.models import ModelManager


class ModelManagerListSerializer(serializers.ModelSerializer):
    """
    模型导入名称，对应数据表的模型集
    实际模型名字通过【模型集】+ 【版本输出】

    """
    class Meta:
        model = ModelManager
        fields = '__all__'


class ModelManagerDetailSerializer(ModelManagerListSerializer):
    pass


class ModelManagerCreateSerializer(serializers.ModelSerializer):

    """
    """

    class Meta:
        model = ModelManager
        fields = (
            'title', 'model', 'organization', 'version', 'project', 'url',
            'type', 'created_by', 'description',
        )


class ModelManagerUpdateSerializer(serializers.ModelSerializer):

    """
    """

    class Meta:
        model = ModelManager
        fields = (
            'model_set', 'organization', 'version',
            'type', 'created_by', 'description',
        )


# def validate_label_config(self, config):
#     Project.validate_label_config(config)
#     return config

