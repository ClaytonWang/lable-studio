#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : serializers_train.py
  > CreateTime : 2022/8/3 09:07
"""
import datetime
from django.utils.timezone import utc
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import SerializerMethodField
from users.serializers import UserSimpleSerializer
from projects.serializers_set import ProjectSetDetailSerializer
from model_manager.models import ModelTrain
from core.redis import redis_get, redis_set, redis_healthcheck
MODEL_TRAIN_AVERAGE_TIME_KEY = 'MODEL_TRAIN_AVERAGE_TIME'
MODEL_TRAIN_EXPIRE_TIME = 60 * 60 * 24


def average_time() -> float:
    """
    平均时间写到Redis，设置固定的有效时间，
    时间过期重新计算平均时间
    有效时间默认一周
    计算数据默认取最新的10个模型计算
    没有训练模型，使用配置文件的默认数值
    :return:
    """
    from django.conf import settings
    _avg = redis_get(MODEL_TRAIN_AVERAGE_TIME_KEY)
    _avg = _avg.decode('utf-8') if _avg and isinstance(_avg, bytes) else _avg
    if not _avg:
        if redis_healthcheck():
            query = ModelTrain.objects.filter(state=4, is_train=True).order_by('-created_at')[:10]
            train_average = []
            for item in query:
                finished = item.train_finished_at if item.train_finished_at else item.updated_at
                time_dt = finished - item.created_at
                avg_time = round(time_dt.seconds / item.train_task.count(), 2)
                train_average.append(avg_time)
            if train_average:
                _avg = round(sum(train_average) / len(train_average), 2)
            else:
                _avg = getattr(settings, 'MODEL_TRAIN_INDIVIDUAL_TASK_TIME')
            redis_set(MODEL_TRAIN_AVERAGE_TIME_KEY, _avg, MODEL_TRAIN_EXPIRE_TIME)
        else:
            _avg = getattr(settings, 'MODEL_TRAIN_INDIVIDUAL_TASK_TIME')
    return float(_avg)


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
    training_progress = SerializerMethodField()

    @staticmethod
    def get_training_progress(obj):
        if obj.state == 3:
            avg = average_time()
            dt = datetime.datetime.now(tz=utc) - obj.created_at
            total_time = avg * obj.train_task.count()
            if total_time <= 0:
                return None
            else:
                _rate = round(dt.seconds / total_time, 2)
            return _rate if _rate < 1 else 0.99
        # 训练完成
        elif obj.state == 4:
            return 1
        else:
            return None

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
    model_id = serializers.IntegerField(required=False)
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
            'model_parameter', 'model_title']


class ModelTrainUpdateSerializer(ModelTrainCreateSerializer):

    """
    """
    pass


class ModelTrainAccuracySerializer(serializers.ModelSerializer):

    created_by = UserSimpleSerializer(default={})
    model_title = serializers.SerializerMethodField()
    model_version = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()

    @staticmethod
    def get_model_title(obj):
        return obj.model.title
        pass

    @staticmethod
    def get_model_version(obj):
        return obj.model.version

    @staticmethod
    def get_project_title(obj):
        return obj.project.title

    class Meta:
        model = ModelTrain
        fields = [
            'model_title', 'model_version', 'project_title',
            'accuracy_rate', 'created_at', 'created_by'
        ]

