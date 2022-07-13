#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : services.py
  > CreateTime : 2022/7/7 08:44
"""
from enum import Enum
from tasks.models import Task
from django.db.transaction import atomic
from tasks.models import Prediction, PredictionDraft
from tasks.models import TaskDbAlgorithm, TaskDbAlgorithmDraft
PREDICTION_BACKUP_FIELDS = [
    'result', 'score', 'model_version', 'task', 'created_at', 'updated_at'
]
CLEAN_ALGORITHM_BACKUP_FIELDS = [
    'source', 'algorithm', 'manual', 'state', 'task', 'project',
    'created_at', 'updated_at', 'updated_by', 'created_by',
]


DB_ALGORITHM_EXPIRE_TIME = 5  # 5秒
DB_ALGORITHM_CANCELED_EXPIRE_TIME = 60 * 2  # 2分钟


class AlgorithmState(str, Enum):
    STARTED = 'started'
    ONGOING = 'ongoing'
    FINISHED = 'finished'
    CANCELED = 'canceled'
    STOPPED = 'stopped'
    FAILED = 'failed'


def rollback_clean(project_id):
    queryset = TaskDbAlgorithmDraft.objects.filter(project_id=project_id).all()
    with atomic():
        update_objs = []
        # query = TaskDbAlgorithm.objects.filter(project_id=project_id).all()
        # 查询上费时，后续优化吧
        for item in queryset:
            query = TaskDbAlgorithm.objects.filter(task=item.task).first()
            if not query:
                continue
            for field in CLEAN_ALGORITHM_BACKUP_FIELDS:
                setattr(query, field, getattr(item, field))
            update_objs.append(query)
        TaskDbAlgorithm.objects.bulk_update(
            update_objs, CLEAN_ALGORITHM_BACKUP_FIELDS
        )
        TaskDbAlgorithmDraft.objects.filter(project_id=project_id).delete()


def rollback_prediction(project_id):
    query_task = Task.objects.filter(project_id=project_id)
    # task_ids = [item.id for item in query]
    queryset = PredictionDraft.objects.filter(task__in=query_task).all()
    with atomic():
        Prediction.objects.filter(task__in=query_task).delete()
        objs = []
        for item in queryset:
            data = dict()
            for field in PREDICTION_BACKUP_FIELDS:
                data[field] = getattr(item, field)
            objs.append(Prediction(**data))
        Prediction.objects.bulk_create(objs)
        PredictionDraft.objects.filter(task__in=query_task).delete()


def save_raw_data(queryset, draft_model, fields):
    draft = []
    for item in queryset:
        data = dict()
        for field in fields:
            data[field] = getattr(item, field)
        draft.append(draft_model(**data))
    draft_model.objects.bulk_create(draft)


def generate_redis_key(algorithm_name: str, project_id: str) -> str:
    return f'DB_ALGORITHM_{algorithm_name}_{project_id}'
