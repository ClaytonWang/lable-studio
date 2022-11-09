"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import datetime

import os
import uuid
import ujson as json
from django.db.models import Avg

from rest_framework import serializers
from django.db import transaction

from data_manager.models import View, Filter, FilterGroup
from tasks.models import Task
from tasks.serializers import TaskSerializer, AnnotationSerializer, \
    PredictionModelSerializer, AnnotationDraftSerializer
from projects.models import Project
from label_studio.core.utils.common import round_floats
from tasks.models import Annotation, Prediction, TaskLabelHistory
from tasks.history_serializer import LabelListSerializer
from projects.models import PromptResult
from model_manager.models import CLEAN_MODEL_FLAG
from db_ml.services import get_choice_values
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = "__all__"


class FilterGroupSerializer(serializers.ModelSerializer):
    filters = FilterSerializer(many=True)

    class Meta:
        model = FilterGroup
        fields = "__all__"


class ViewSerializer(serializers.ModelSerializer):
    filter_group = FilterGroupSerializer(required=False)

    class Meta:
        model = View
        fields = "__all__"

    def to_internal_value(self, data):
        """
        map old filters structure to models
        "filters": {  ===> FilterGroup model
            "conjunction": "or",
            "items":[  ===> "filters" in FilterGroup
                 {  ==> Filter model
                   "filter":"filter:tasks:data.image", ==> column
                    "operator":"contains",
                    "type":"Image",
                    "value": <string: "XXX" | int: 123 | dict | list>
                 },
                  {
                    "filter":"filter:tasks:data.image",
                    "operator":"equal",
                    "type":"Image",
                    "value": <string: "XXX" | int: 123 | dict | list>
                 }
              ]
           }
        }
        """
        _data = data.get("data", {})

        filters = _data.pop("filters", {})
        conjunction = filters.get("conjunction")
        if "filter_group" not in data and conjunction:
            data["filter_group"] = {"conjunction": conjunction, "filters": []}
            if "items" in filters:
                for f in filters["items"]:
                    data["filter_group"]["filters"].append(
                        {
                            "column": f.get("filter", ""),
                            "operator": f.get("operator", ""),
                            "type": f.get("type", ""),
                            "value": f.get("value", {}),
                        }
                    )

        ordering = _data.pop("ordering", {})
        data["ordering"] = ordering

        return super().to_internal_value(data)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        filters = result.pop("filter_group", {})
        if filters:
            filters["items"] = []
            filters.pop("filters", [])
            filters.pop("id", None)

            for f in instance.filter_group.filters.order_by("index"):
                filters["items"].append(
                    {
                        "filter": f.column,
                        "operator": f.operator,
                        "type": f.type,
                        "value": f.value,
                    }
                )
            result["data"]["filters"] = filters

        selected_items = result.pop("selected_items", {})
        if selected_items:
            result["data"]["selectedItems"] = selected_items

        ordering = result.pop("ordering", {})
        if ordering:
            result["data"]["ordering"] = ordering
        return result

    @staticmethod
    def _create_filters(filter_group, filters_data):
        filter_index = 0
        for filter_data in filters_data:
            filter_data["index"] = filter_index
            filter_group.filters.add(Filter.objects.create(**filter_data))
            filter_index += 1

    def create(self, validated_data):
        with transaction.atomic():
            filter_group_data = validated_data.pop("filter_group", None)
            if filter_group_data:
                filters_data = filter_group_data.pop("filters", [])
                filter_group = FilterGroup.objects.create(**filter_group_data)

                self._create_filters(filter_group=filter_group, filters_data=filters_data)

                validated_data["filter_group_id"] = filter_group.id
            view = View.objects.create(**validated_data)

            return view

    def update(self, instance, validated_data):
        with transaction.atomic():
            filter_group_data = validated_data.pop("filter_group", None)
            if filter_group_data:
                filters_data = filter_group_data.pop("filters", [])

                filter_group = instance.filter_group
                if filter_group is None:
                    filter_group = FilterGroup.objects.create(**filter_group_data)

                conjunction = filter_group_data.get("conjunction")
                if conjunction and filter_group.conjunction != conjunction:
                    filter_group.conjunction = conjunction
                    filter_group.save()

                filter_group.filters.clear()
                self._create_filters(filter_group=filter_group, filters_data=filters_data)

            ordering = validated_data.pop("ordering", None)
            if ordering and ordering != instance.ordering:
                instance.ordering = ordering
                instance.save()

            if validated_data["data"] != instance.data:
                instance.data = validated_data["data"]
                instance.save()

            return instance


class CustomViewSerializer(ViewSerializer):

    def update(self, instance, validated_data):
        with transaction.atomic():
            filter_group_data = validated_data.pop("filter_group", None)
            if filter_group_data:
                filters_data = filter_group_data.pop("filters", [])
                # 修改新加的两个字段 manual_label auto_label
                for index, item in enumerate(filters_data):
                    column = item.get('column')
                    if column and column.endswith(':manual_label'):
                        column = column.replace(':manual_label', ':annotations_results')
                        filters_data[index]['column'] = column
                    elif column and column.endswith(':auto_label'):
                        column = column.replace(':auto_label', ':predictions_results')
                        filters_data[index]['column'] = column

                filter_group = instance.filter_group
                if filter_group is None:
                    filter_group = FilterGroup.objects.create(**filter_group_data)

                conjunction = filter_group_data.get("conjunction")
                if conjunction and filter_group.conjunction != conjunction:
                    filter_group.conjunction = conjunction
                    filter_group.save()

                filter_group.filters.clear()
                self._create_filters(filter_group=filter_group, filters_data=filters_data)

            ordering = validated_data.pop("ordering", None)
            # 修改新加的两个字段
            # manual_label auto_label
            if ordering:
                for index, item in enumerate(ordering):
                    # tasks: avg_lead_time
                    if 'manual_label' in item:
                        ordering[index] = item.replace(
                            'manual_label', 'annotations_results'
                        )
                    elif 'auto_label' in item:
                        ordering[index] = item.replace(
                            'auto_label', 'predictions_results'
                        )

            if ordering and ordering != instance.ordering:
                instance.ordering = ordering
                instance.save()

            if validated_data["data"] != instance.data:
                instance.data = validated_data["data"]
                instance.save()

            return instance


class DataManagerTaskSerializer(TaskSerializer):
    predictions = serializers.SerializerMethodField(required=False, read_only=True)
    annotations = serializers.SerializerMethodField(required=False, read_only=True)
    drafts = serializers.SerializerMethodField(required=False, read_only=True)
    annotators = serializers.SerializerMethodField(required=False, read_only=True)

    inner_id = serializers.IntegerField(required=False)
    cancelled_annotations = serializers.IntegerField(required=False)
    total_annotations = serializers.IntegerField(required=False)
    total_predictions = serializers.IntegerField(required=False)
    completed_at = serializers.DateTimeField(required=False)
    annotations_results = serializers.SerializerMethodField(required=False)
    predictions_results = serializers.SerializerMethodField(required=False)
    predictions_score = serializers.FloatField(required=False)
    file_upload = serializers.SerializerMethodField(required=False)
    annotations_ids = serializers.SerializerMethodField(required=False)
    predictions_model_versions = serializers.SerializerMethodField(required=False)
    avg_lead_time = serializers.FloatField(required=False)
    updated_by = serializers.SerializerMethodField(required=False, read_only=True)
    # predictions_score = serializers.SerializerMethodField(required=False)
    auto_label = serializers.SerializerMethodField(required=False)
    manual_label = serializers.SerializerMethodField(required=False)
    marked_method = serializers.SerializerMethodField(required=False)
    # clean_method = serializers.SerializerMethodField(required=False)
    auto_label_at = serializers.SerializerMethodField(required=False)

    CHAR_LIMITS = 500
    
    class Meta:
        model = Task
        ref_name = 'data_manager_task_serializer'
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(DataManagerTaskSerializer, self).__init__(*args, **kwargs)

        self.task_ids = [item.id for item in self.instance] if isinstance(
            self.instance, list) else [self.instance.id]

        self.anno_query = Annotation.objects.filter(task_id__in=self.task_ids)
        self.pre_query = Prediction.objects.filter(task_id__in=self.task_ids)
        self.prompt_query = PromptResult.objects.filter(
            task_id__in=self.task_ids
        )

        self.anno_data = {
            str(item['task']): item for item in
            AnnotationSerializer(
                self.anno_query, many=True, read_only=True, default=[]
            ).data
        }
        self.pre_data = {
            str(item['task']): item for item in
            PredictionModelSerializer(
                self.pre_query, many=True, read_only=True, default=[]
            ).data
        }
        self.prompt_data = {
            str(item['task']): item for item in
            self.prompt_query.values(
                'task', 'metrics', 'created_at', 'updated_at'
            )
        }

    def check_update_time(self, obj):
        pre = self.pre_data.get(str(obj.id), {})
        prompt = self.prompt_data.get(str(obj.id), {})
        if not pre and not prompt:
            return None, None

        pre_update_at = pre.get('updated_at', '')
        pre_update_at = datetime.datetime.strptime(
            pre_update_at, UTC_FORMAT
        ).timestamp() if pre_update_at else 0
        prompt_update_at = prompt.get('updated_at', '')
        prompt_update_at = prompt_update_at.replace(tzinfo=None).timestamp() \
            if prompt_update_at else 0
        if pre_update_at > prompt_update_at:
            return 'pre', pre
        else:
            return 'prompt', prompt

    # def get_predictions_score(self, obj):
    #     label, rst = self.check_update_time(obj)
    #     if label == 'pre':
    #         return obj.predictions_score \
    #             if hasattr(obj, 'predictions_score')else None
    #     elif label == 'prompt' and rst:
    #         metrics = rst.get('metrics', {})
    #         return metrics.get('confidence')
    #     else:
    #         return None

    def get_marked_method(self, obj):
        data = self.pre_data.get(str(obj.id), {})
        if not data or not data.get('result'):
            return ''
        # 历史记录
        model = data.get('model', {})
        if model and model.get('type'):
            return model.get('text')
        return ''

        # result = data.get('result', [])
        # if len(result) >= 1:
        #     origin = result[0].get('origin', '')
        #     if origin == 'prompt':
        #         return '提示学习'
        #     elif origin == 'prediction':
        #         return '普通'
        # return ''
    #
    # def get_clean_method(self, obj):
    #     data = self.pre_data.get(str(obj.id), {})
    #     if not data or not data.get('result'):
    #         return ''
    #     model = data.get('model', {})
    #     if model and model.get('type') in CLEAN_MODEL_FLAG:
    #         return model.get('text')
    #     return ''

    def get_auto_label_at(self, obj):
        data = self.pre_data.get(str(obj.id), [])
        if not len(data):
            return ''

        updated_at = data.get('updated_at')
        if updated_at:
            u_dt = datetime.datetime.strptime(
                updated_at, UTC_FORMAT
            )
            return u_dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ''

    def get_auto_label(self, obj):
        """
        自动标注字段：预标注（普通）和提示学习取最新的值
        :param obj:
        :return:
        """
        data = self.pre_data.get(str(obj.id), [])
        result = data.get('result', []) if len(data) else []
        pre_choices = get_choice_values(result)
        return pre_choices

    def get_manual_label(self, obj):
        data = self.anno_data.get(str(obj.id), [])
        if not len(data):
            return ''
        result = data.get('result', []) if len(data) else []
        choices = get_choice_values(result)
        return choices

    def to_representation(self, obj):
        """ Dynamically manage including of some fields in the API result
        """
        ret = super(DataManagerTaskSerializer, self).to_representation(obj)
        if not self.context.get('annotations'):
            ret.pop('annotations', None)
        if not self.context.get('predictions'):
            ret.pop('predictions', None)
        return ret

    def _pretty_results(self, task, field, unique=False):
        if not hasattr(task, field) or getattr(task, field) is None:
            return ''

        result = getattr(task, field)
        if isinstance(result, str):
            output = result
            if unique:
                output = list(set(output.split(',')))
                output = ','.join(output)

        elif isinstance(result, int):
            output = str(result)
        else:
            result = [r for r in result if r is not None]
            if unique:
                result = list(set(result))
            result = round_floats(result)
            output = json.dumps(result, ensure_ascii=False)[1:-1]  # remove brackets [ ]

        return output[:self.CHAR_LIMITS].replace(',"', ', "').replace('],[', "] [").replace('"', '')

    def get_annotations_results(self, task):
        return self._pretty_results(task, 'annotations_results')

    def get_predictions_results(self, task):
        return self._pretty_results(task, 'predictions_results')

    def get_annotations(self, task):
        rst = self.anno_data.get(str(task.id), [])
        return [rst] if rst else []

    def get_predictions(self, task):
        rst = self.pre_data.get(str(task.id))
        return [rst] if rst else []

    @staticmethod
    def get_file_upload(task):
        if not hasattr(task, 'file_upload_field'):
            return None
        file_upload = task.file_upload_field
        return os.path.basename(task.file_upload_field) if file_upload else None

    @staticmethod
    def get_updated_by(obj):
        return [{"user_id": obj.updated_by_id}] if obj.updated_by_id else []

    @staticmethod
    def get_annotators(obj):
        if not hasattr(obj, 'annotators'):
            return []

        annotators = obj.annotators
        if not annotators:
            return []
        if isinstance(annotators, str):
            annotators = [int(v) for v in annotators.split(',')]

        annotators = list(set(annotators))
        annotators = [a for a in annotators if a is not None]
        return annotators if hasattr(obj, 'annotators') and annotators else []

    def get_annotations_ids(self, task):
        return self._pretty_results(task, 'annotations_ids', unique=True)

    def get_predictions_model_versions(self, task):
        return self._pretty_results(task, 'predictions_model_versions', unique=True)

    def get_drafts(self, task):
        """Return drafts only for the current user"""
        # it's for swagger documentation
        if not isinstance(task, Task) or not self.context.get('drafts'):
            return []

        drafts = task.drafts
        if 'request' in self.context and hasattr(self.context['request'], 'user'):
            user = self.context['request'].user
            drafts = drafts.filter(user=user)

        return AnnotationDraftSerializer(drafts, many=True, read_only=True, default=True, context=self.context).data


class TaskDetailSerializer(DataManagerTaskSerializer):

    history = serializers.SerializerMethodField(required=False)

    @staticmethod
    def get_history(obj):
        instance = TaskLabelHistory.objects.filter(task=obj).order_by('-id')
        return LabelListSerializer(instance=instance, many=True).data


class SelectedItemsSerializer(serializers.Serializer):
    all = serializers.BooleanField()
    included = serializers.ListField(child=serializers.IntegerField(), required=False)
    excluded = serializers.ListField(child=serializers.IntegerField(), required=False)

    def validate(self, data):
        if data["all"] is True and data.get("included"):
            raise serializers.ValidationError("included not allowed with all==true")
        if data["all"] is False and data.get("excluded"):
            raise serializers.ValidationError("excluded not allowed with all==false")

        view = self.context.get("view")
        request = self.context.get("request")
        if view and request and request.method in ("PATCH", "DELETE"):
            all_value = view.selected_items.get("all")
            if all_value and all_value != data["all"]:
                raise serializers.ValidationError("changing all value possible only with POST method")

        return data


class ViewResetSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
