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
from projects.models import ProjectSummary
from projects.models import Project
from model_manager.services import ml_backend_request
from model_manager.models import ModelManager
from model_manager.services import ml_backend_params

INTENT_DIALOG_PROMPT_TOKEN = '101469da9d088219'
CONVERSATIONAL_GENERATION_TOKEN = '9e72f8c5aa27811d'

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


def redis_update_finish_state(redis_key, redis_data, count=0):
    finish = int(redis_data.get('finish', 0)) + 1
    if count != 0 and finish < count:
        finish = count
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
        _type = item.get('type')
        if _type == 'choices':
            tmp_choices = item.get('value', {}).get('choices', [])
        elif _type == 'textarea':
            tmp_choices = item.get('value', {}).get('text', [])

        if not tmp_choices:
            continue
        choices += tmp_choices
    return choices


def get_project_labels(project_id):
    project = Project.objects.filter(id=project_id).first()
    labels = []
    if project and project.parsed_label_config:
        parsed_label_config = project.parsed_label_config
        intent = parsed_label_config.get('intent', {})
        labels = intent.get('labels', {})
        if isinstance(labels, list):
            return labels
        elif isinstance(labels, dict):
            return list(labels.keys())
    return labels

    # summary = ProjectSummary.objects.filter(project_id=project_id).first()
    # labels = []
    # for k in summary.created_annotations:
    #     for item in k.split('|'):
    #         vls = summary.created_labels.get(item)
    #         if not vls:
    #             continue
    #         labels += list(vls.keys())
    #
    # return {index: value for index, value in enumerate(labels)}


def generate_uuid(algorithm_type, project_id):
    _uuid = uuid.uuid4()
    return f'{_uuid}_{algorithm_type}_{project_id}'


def predict_prompt(
        project_id, model_id, task_data, _uuid, template=[], return_num=0,
        prompt_type=None
):
    """
    预标注（普通）
    预标注（0样本） 提示学习
    :param project_id:
    :param model_id:
    :param task_data:
    :param template:
    :param _uuid:
    :param return_num:
    :param prompt_type:
    :return:
    """
    if prompt_type == 'intent-dialog':
        # 预标注（0样本）
        model = get_first_version_model(INTENT_DIALOG_PROMPT_TOKEN)
    elif prompt_type == 'conversational-generation':
        # 生成对话（0样本）
        model = get_first_version_model(CONVERSATIONAL_GENERATION_TOKEN)
    else:
        # 预标注普通   生成对话普通   前端有选择模型
        model = ModelManager.objects.filter(id=model_id).first()
    _params = dict()
    _json = ml_backend_params(
        data=task_data,
        labels=get_project_labels(project_id),
        templates=template,
        extra=dict(return_nums=return_num)
    )

    return ml_backend_request(
        model.url, uri=['predict', _uuid], params=_params,
        _json=_json, method="post"
    )


def get_first_version_model(token, version=1.0):
    return ModelManager.objects.filter(
        token=token, version=version
    ).order_by('-id').first()


def preprocess_clean(project_id, model_ids, task_data, _uuid):
    if model_ids:
        model_query = ModelManager.objects.filter(id__in=model_ids).values(
            'id', 'url', 'title')
    else:
        tokens = ['130a104f9fd7d257', '71da5487bb41d24c', '5c69636f596635f3']
        model_query = ModelManager.objects.filter(
            token__in=tokens
        ).values('id', 'url', 'title', 'token')
        model_ids = []
        for token in tokens:
            for model in model_query:
                if token != model['token']:
                    continue
                model_ids.append(model['id'])
                break

    if len(model_ids) != len(model_query):
        return False, f'{str(model_ids)}模型没有查询到模型'

    model_data = {item['id']: item['url'] for item in model_query}
    urls = [model_data[_id] for _id in model_ids]
    first_url = urls.pop(0)

    # _params = dict(uuid=_uuid)
    _params = {}
    _json = ml_backend_params(
        data=task_data,
        labels=get_project_labels(project_id),
        extra=dict(
            pipelines=urls
        )
    )
    return ml_backend_request(
        first_url, uri=['pipeline', _uuid], params=_params, _json=_json,
        method='post',
    )


def train_model(
        project_id, model_id, task_data, _uuid, template=[], return_num=0,
        **kwargs
):
    if model_id:
        model = ModelManager.objects.filter(id=model_id).first()
    else:
        model = get_first_version_model(INTENT_DIALOG_PROMPT_TOKEN)

    _params = dict()
    extra = dict(return_nums=return_num)
    if kwargs.get('model_parameter'):
        extra.update(**kwargs.get('model_parameter', {}))
    _json = ml_backend_params(
        data=task_data,
        labels=get_project_labels(project_id),
        templates=template,
        extra=extra
    )

    return ml_backend_request(
        model.url, uri=['train', _uuid], params=_params,
        _json=_json, method="post"
    )


def train_failure_delete_train_model(model_train_id):
    from model_manager.models import ModelTrain, ModelManager

    train = ModelTrain.objects.filter(id=model_train_id).first()
    if not train:
        return

    train.assessment_task.all().delete()
    train.train_task.all().delete()
    train.new_model and train.new_model.delete()
    train.delete()
