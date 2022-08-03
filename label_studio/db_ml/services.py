#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : services.py
  > CreateTime : 2022/7/7 08:44
"""
import uuid

from enum import Enum
import json
from tasks.models import Task
from core.redis import redis_set, redis_get
from django.db.transaction import atomic
from tasks.models import Prediction, PredictionDraft
from tasks.models import TaskDbAlgorithm, TaskDbAlgorithmDraft
from projects.models import PromptResultDraft, PromptResult
from model_manager.services import ml_backend_request
from model_manager.models import ModelManager

PREDICTION_BACKUP_FIELDS = [
    'result', 'score', 'model_version', 'task', 'created_at', 'updated_at'
]
CLEAN_ALGORITHM_BACKUP_FIELDS = [
    'source', 'algorithm', 'manual', 'state', 'task', 'project',
    'created_at', 'updated_at', 'updated_by', 'created_by',
]
PROMPT_BACKUP_FIELDS = [
    'project', 'task', 'metrics', 'created_at', 'updated_at'
]


DB_ALGORITHM_EXPIRE_TIME = 5  # 5秒
DB_ALGORITHM_CANCELED_EXPIRE_TIME = 60 * 2  # 2分钟
DB_TASK_RUNNING_TIME = 60 * 60 * 12


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
        # 查询上 费时，后续优化吧
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


def rollback_prompt(project_id):
    queryset = PromptResultDraft.objects.filter(project_id=project_id).all()
    with atomic():
        PromptResult.objects.filter(project_id=project_id).delete()
        objs = []
        for item in queryset:
            data = dict()
            for field in PREDICTION_BACKUP_FIELDS:
                data[field] = getattr(item, field)
            objs.append(PromptResult(**data))
        PromptResult.objects.bulk_create(objs)
        PromptResultDraft.objects.filter(project_id=project_id).delete()


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


def redis_set_json(key, data, expire=DB_TASK_RUNNING_TIME):
    redis_set(key, json.dumps(data, ensure_ascii=False), expire)


def redis_get_json(key):
    data = redis_get(key)
    return json.loads(bytes.decode(data)) if data else {}


def redis_update_finish_state(redis_key, redis_data):
    finish = int(redis_data.get('finish', 0)) + 1
    redis_data['finish'] = finish
    if finish == int(redis_data.get('total', 0)):
        redis_data['state'] = AlgorithmState.FAILED
    redis_set_json(redis_key, redis_data)


def update_prediction_data(task_id, prompt_data=None):
    """
    prompt 生成的数据写回 prediction 表
     result = {
        "task": text + kwargs.get('template', ''),
        "annotation": res_text,
        "confidence": confidence,
        "average": {"正面标签": np.random.rand(), "负面标签": np.random.rand()},
        "output":
            [
                {"template": "你好，我是模版A1",
              "label": "正面",
              # "score": "烂片%f" % np.random.rand(),
              # "wgtedAvg": np.random.rand()
                 },
             {
                 "template": "你好，我是模版B",
              "label": "负面",
              "score": "精品%f" % np.random.rand(),
              "wgtedAvg": np.random.rand()}
             ]
    }
    :param task_id:
    :param prompt_data:
    :return:
    """
    task = Task.objects.filter(id=task_id).first()
    if not task:
        return
    annotation = prompt_data.get('annotation')
    confidence = prompt_data.get('confidence')
    pre_result = {
        'origin': 'prompt',
        'from_name': 'intent',
        'to_name': 'dialogue',
        'type': 'choices',
        'value': {
            'choices': [annotation], 'start': 0, 'end': 1
        },
    }
    tag_data = dict(
        task=task,
        result=[pre_result],
        score=round(confidence, 4),

    )
    obj, is_created = Prediction.objects.update_or_create(
        defaults=tag_data, task=task
    )
    print('prompt write prediction table msg: ', is_created, str(tag_data))
    pass


def get_choice_values(result):
    """
    解析result 的choices
    [{'type': 'choices', 'value': {'end': 1, 'start': 0, 'choices': ['肯定']}, 'to_name': 'dialogue', 'from_name': 'intent'}]
    :param result:
    :return:
    """
    choices = []
    for item in result:
        tmp_choices = item.get('value', {}).get('choices', [])
        if not tmp_choices:
            continue
        choices += tmp_choices
    return choices


def generate_uuid():
    return uuid.uuid4()


def predict_prompt(model_id, project_id, task_data):
    """
    预标注（普通）
    预标注（0样本） 提示学习
    :param model_id:
    :param project_id:
    :param task_data:
    :return:
    """
    model = ModelManager.objects.filter(id=model_id).first()
    _params = dict(
        uuid=f'{generate_uuid()}_{project_id}'
    )
    _json = dict(data=task_data)
    return ml_backend_request(
        model.url, uri=[], params=_params, json=_json
    )

