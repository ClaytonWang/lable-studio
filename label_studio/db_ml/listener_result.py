#!/usr/bin/env python
# encoding: utf-8

"""
  http://redisdoc.com/topic/notification.html
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : algorithm_result.py
  > CreateTime : 2022/8/4 08:27
"""
import json
import logging
from core.redis import redis_get
from tasks.models import Prediction
from tasks.models import TaskDbAlgorithm
from projects.models import PromptResult
from db_ml.services import AlgorithmState
from db_ml.services import generate_redis_key
from db_ml.services import redis_set_json, redis_get_json
from db_ml.services import redis_update_finish_state
from db_ml.services import update_prediction_data
logger = logging.getLogger(__file__)

"""


"""


def process_celery_result(key):
    """
    celery status
    CELERY STATE
    PENDING  等待
    STARTED  开始
    RETRY    重试

    SUCCESS  成功

    FAILURE  失败
    REVOKED  撤销

    :param key:
    :return:
    """
    k_result = redis_get(key)
    k_result = json.loads(str(k_result, 'utf-8'))
    # 状态判断 不符合处理的状态丢弃

    logger.info(f'Redis message: {k_result}')
    task_status = k_result.get('status')

    if task_status in ('PENDING', 'STARTED', 'RETRY'):
        return

    if task_status in ('FAILURE', 'REVOKED'):
        k_result['result'] = ''

    # project 和 task ID 是否有效后期判断

    algorithm_type, project_id, task_id = split_project_and_task_id(key)
    if not task_id or not project_id:
        logger.warning(
            f"Invalid project id or task id."
            f" project:{project_id} task:{task_id}"
        )
        return

    algorithm_result = k_result.get('result')
    if algorithm_type == 'prediction-intent':
        data = get_prediction_intent_df(algorithm_result, task_id)
        insert_prediction_value(data, project_id, task_id)
    elif algorithm_type == 'prediction-generate':
        data = get_prediction_generate_df(algorithm_result, task_id)
        insert_prediction_value(data, project_id, task_id)
    elif algorithm_type == 'prompt-intent':
        insert_prompt_intent_value(algorithm_result, project_id, task_id)
    elif algorithm_type == 'prompt-generate':
        insert_prompt_generate_value()
    elif algorithm_type == 'clean':
        insert_clean_value(algorithm_result, project_id, task_id)
    else:
        logger.info(f'Invalid algorithm_type: {algorithm_type}')


def split_project_and_task_id(celery_task_id) -> list:
    """
    celery-task-met_{uuid}_{algorithm_type}_{project_id}_{task_id}'
    :param celery_task_id:
    :return:
    """
    uuid, algorithm_type, project_id, task_id = None, None, None, None
    try:
        ids = celery_task_id.split('_')
        if len(ids) == 5:
            _, uuid, algorithm_type, project_id, task_id = ids
        elif len(ids) == 4:
            _, uuid, algorithm_type, project_id = ids
    except Exception as e:
        logger.warning(
            f'Redis receive celery id :{celery_task_id} \n exception msg:{e}'
        )
    return [algorithm_type, project_id, task_id]


def insert_prediction_value(data, project_id, task_id):
    """
    celery result
    {
        "status":"SUCCESS",
        "result":["肯定", 0.42131],
        "traceback":null,
        "children":[],
        "date_done":"2022-08-04T04:43:40.201419",
        "task_id":"uuid_test-460"
    }

    :param project_id:
    :param task_id:
    :param data:
    :return:
    """
    tag_data = data
    print(f"results: ....{str(tag_data)}")
    redis_key = generate_redis_key('prediction', project_id)
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        obj, is_created = Prediction.objects.update_or_create(
            defaults=tag_data, task=task_id
        )
        redis_update_finish_state(redis_key, p_state)
        print('obj:', obj.id, ' is_ created:', is_created)


def get_prediction_intent_df(algorithm_result, task_id):
    annotation = algorithm_result[0]
    confidence = algorithm_result[1]
    pre_result = {
        'origin': 'prediction',
        'from_name': 'intent',
        'to_name': 'dialogue',
        'type': 'choices',
        'value': {
            'choices': [annotation], 'start': 0, 'end': 1
        },
    }
    tag_data = dict(
        task=task_id,
        result=[pre_result],
        score=round(confidence, 4),

    )
    return tag_data


def get_prediction_generate_df(algorithm_result, task_id):
    pre_result = {
        'origin': 'prediction',
        'from_name': 'response',
        'to_name': 'chat',
        "type": "textarea",
        'value': {
            "text": algorithm_result,
        },
    }
    tag_data = dict(
        task=task_id,
        result=[pre_result],
    )
    return tag_data


def insert_prompt_intent_value(algorithm_result, project_id, task_id):
    """
    :param algorithm_result:
    :param project_id:
    :param task_id:
    :return:
    """

    # annotation, confidence = '', 0
    annotation = algorithm_result[0]
    confidence = algorithm_result[1]
    result = {
        "task": '',
        "annotation": annotation,
        "confidence": confidence,
        "average": '',
        "output": []
    }
    redis_key = generate_redis_key('prompt', project_id)
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        update_prediction_data(task_id, result)
        c = PromptResult(
            project_id=project_id,
            task_id=task_id,
            metrics=result
        )
        c.save()
        redis_update_finish_state(redis_key, p_state)


def insert_prompt_generate_value(algorithm_result, project_id, task_id):

    text = []
    for sub_text in algorithm_result:
        for _text in sub_text:
            text.append(_text)

    pre_result = {
        'origin': 'prediction',
        'from_name': 'response',
        'to_name': 'chat',
        "type": "textarea",
        'value': {
            "text": text,
        },
    }
    tag_data = dict(
        task=task_id,
        result=[pre_result],
    )

    redis_key = generate_redis_key('prompt', project_id)
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        update_prediction_data(task_id, tag_data)
        c = PromptResult(
            project_id=project_id,
            task_id=task_id,
            metrics=algorithm_result
        )
        c.save()
        redis_update_finish_state(redis_key, p_state)


def insert_clean_value(algorithm_result, project_id, task_id):
    """
    "result":[
         {
            'task_id': 450,
            'dialogue': [
                   {'text': '好的，请问您还有其他业务需要办理吗？', 'author': 'a'},
                   {'text': '查套餐.查语音.查流量？', 'author': 'b'},
                   {'text': '正在为您办理XXX业务，业务套餐为XXX元xxx分钟包含XX兆流量', 'author': 'a'},
                   {'text': '您的XXX业务办理成功，请问您还有其他业务需要办理查询吗', 'author': 'b'},
             ]
         }
    ]

    :param algorithm_result:
    :param project_id:
    :param task_id:
    :return:
    """
    dialogue = algorithm_result[0].get('dialogue', []) \
        if len(algorithm_result) else []
    try:

        redis_key = generate_redis_key('clean', project_id)
        p_state = redis_get_json(redis_key)
        if p_state and p_state.get('state') == AlgorithmState.ONGOING:
            TaskDbAlgorithm.objects.filter(task_id=task_id).update(
                algorithm=dialogue, state=2, remarks=''
            )
            redis_update_finish_state(redis_key, p_state)
    except Exception as e:
        TaskDbAlgorithm.objects.filter(task_id=task_id).update(
            state=3, remarks=str(e)
        )
