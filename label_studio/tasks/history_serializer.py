# -*- coding: utf-8 -*-
"""
    >File    : history_serializer.py
    >Author  : YJD
    >Mail    : jindu.yin@digitalbrain.cn
    >Time    : 2022/11/8 13:57
"""

from tasks.models import TaskLabelHistory
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from model_manager.serializers import ModelManagerSubDetailSerializer
from db_ml.services import get_choice_values


class LabelListSerializer(ModelSerializer):

    model = ModelManagerSubDetailSerializer()
    result = SerializerMethodField()

    @staticmethod
    def get_result(obj):
        return get_choice_values(obj.result)

    class Meta:
        model = TaskLabelHistory
        fields = '__all__'

