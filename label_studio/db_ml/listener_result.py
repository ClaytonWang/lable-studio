#!/usr/bin/env python
# encoding: utf-8

"""
  http://redisdoc.com/topic/notification.html
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : algorithm_result.py
  > CreateTime : 2022/8/4 08:27
"""
import datetime
import json
import logging
from django.db.models import Q
from core.redis import redis_get
from projects.models import Project
from tasks.models import Task
from tasks.models import Prediction
from tasks.models import TaskDbAlgorithm
from tasks.models import Annotation
from projects.models import PromptResult
from db_ml.services import AlgorithmState
from db_ml.services import generate_redis_key
from db_ml.services import redis_set_json, redis_get_json
from db_ml.services import redis_update_finish_state
from db_ml.services import update_prediction_data
from db_ml.services import train_failure_delete_train_model
from model_manager.models import ModelTrain, ModelManager
from core.redis import _redis, redis_get, redis_set, redis_delete
logger = logging.getLogger('db')

"""


"""


def read_redis_data(project_id, algorithm_type):
    fuzzy_key = f'celery-task-meta*_{algorithm_type}_{project_id}_*'
    for key in _redis.scan_iter(fuzzy_key):
        try:
            key = key.decode('utf-8')
            k_result = redis_get(key)
            k_result = json.loads(str(k_result, 'utf-8'))
            status = k_result.get('status')
            result = k_result.get('result', '')
            print(k_result)
            data = dict(
                celery_task_id=key,
                status=status,
                result=result
            )
            process_callback_result(data)
        except Exception as e:
            print(f'ML Exception: {e} celery_task_id {key}')
        finally:
            redis_delete(key)
            pass


def process_callback_result(data):
    task_status = data.get('status')
    celery_task_id = data.get('celery_task_id')
    result = data.get('result')
    print(f'ML return message: {data}')
    if task_status in ('PENDING', 'STARTED', 'RETRY'):
        print(f'ML celery task id : {celery_task_id}  status: {task_status}')
        return

    algorithm_type, project_id, task_id = split_project_and_task_id(celery_task_id)
    print(' algorithm_type: ', algorithm_type, ' project_id: ', project_id, ' task_id: ', task_id)
    if algorithm_type == 'train' and task_status == 'FAILURE':
        train_failure_delete_train_model(project_id)
        print(f'ML Train Task status is failed. {celery_task_id}')
    else:
        if task_status in ['SUCCESS']:
            process_algorithm_result(algorithm_type, project_id, task_id, result)
        else:
            print(f'ML Task status is failed. {celery_task_id}')


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
    process_algorithm_result(algorithm_type, project_id, task_id, algorithm_result)


def process_algorithm_result(algorithm_type, project_id, task_id, algorithm_result):
    """

    :param algorithm_type:
    :param project_id:
    :param task_id:
    :param algorithm_result:
    :return:
    """
    if algorithm_type == 'train':
        #
        """
        train 时，project_id带的是modelTrain的主键
         {port: 100010}
        """
        insert_train_model(algorithm_result, project_id)
    else:
        project = Project.objects.filter(id=project_id).first()
        if not project:
            logger.info(f'Invalid project id : {project_id}')
            return
        if project.template_type == 'intent-dialog':
            if algorithm_type == 'prediction':
                data = get_prediction_intent_df(algorithm_result, task_id)
                insert_prediction_value(data, project_id, task_id)
            elif algorithm_type == 'prompt':
                insert_prompt_intent_value(algorithm_result, project_id, task_id)
            elif algorithm_type == 'clean':
                insert_clean_value(algorithm_result, project_id, task_id)
        elif project.template_type == 'conversational-generation':
            if algorithm_type == 'prediction':
                data = get_prediction_generate_df(algorithm_result, task_id)
                insert_prediction_value(data, project_id, task_id)
            elif algorithm_type == 'prompt':
                insert_prompt_generate_value(algorithm_result, project_id, task_id)
        else:
            logger.info(f'Invalid algorithm_type: {algorithm_type}')


def split_project_and_task_id(celery_task_id) -> list:
    """
    celery-task-met_{uuid}_{algorithm_type}_{project_id}_{task_id}'
    :param celery_task_id:
    :return:
    """
    "celery-task-meta-d648d0ea-469b-4eff-96d4-529920fec100_prediction_83_811"
    uuid, algorithm_type, project_id, task_id = None, None, None, None
    try:
        ids = celery_task_id.split('_')
        if len(ids) == 4:
            _, algorithm_type, project_id, task_id = ids
        elif len(ids) == 3:
            _, algorithm_type, project_id = ids
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
            defaults=tag_data, task_id=task_id
        )
        finish_task_count = Prediction.objects.filter(
            task__in=Task.objects.filter(project_id=project_id)
        ).count()
        redis_update_finish_state(redis_key, p_state, count=finish_task_count)
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
        task_id=task_id,
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
        task_id=task_id,
        result=[pre_result],
    )
    return tag_data


def insert_prompt_intent_value(algorithm_result, project_id, task_id):
    """
    预标注 0样本
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
        finish_task_count = PromptResult.objects.filter(
            project_id=project_id
        ).count()
        redis_update_finish_state(redis_key, p_state, count=finish_task_count)


def insert_prompt_generate_value(algorithm_result, project_id, task_id):
    """
    对话生成 0样本
    :param algorithm_result:
    :param project_id:
    :param task_id:
    :return:
    """
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
        task_id=task_id,
        result=[pre_result],
    )
    redis_key = generate_redis_key('prompt', project_id)
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        a, is_created = Prediction.objects.update_or_create(
            defaults=tag_data, task_id=task_id
        )
        print(f'prompt Prediction result: {a} {is_created}')

        c = PromptResult(
            project_id=project_id,
            task_id=task_id,
            metrics=algorithm_result
        )
        c.save()
        finish_task_count = PromptResult.objects.filter(
            project_id=project_id
        ).count()
        redis_update_finish_state(redis_key, p_state, count=finish_task_count)


def insert_clean_value(algorithm_result, project_id, db_algorithm_id):
    """
     'result': [{'text': '您好，女士，我这边看到了，他每个月给您扣取的费用都是正常费用，您的正常的月费用的。', 'author': ''}],

    "result":
         {
            'task_id': 450,
            'dialogue': [
                   {'text': '好的，请问您还有其他业务需要办理吗？', 'author': 'a'},
                   {'text': '查套餐.查语音.查流量？', 'author': 'b'},
                   {'text': '正在为您办理XXX业务，业务套餐为XXX元xxx分钟包含XX兆流量', 'author': 'a'},
                   {'text': '您的XXX业务办理成功，请问您还有其他业务需要办理查询吗', 'author': 'b'},
             ]
         }


    :param algorithm_result:
    :param project_id:
    :param db_algorithm_id:
    :return:
    """
    if 'dialogue' in algorithm_result:
        dialogue = algorithm_result.get('dialogue', [])
    else:
        dialogue = algorithm_result
    try:
        redis_key = generate_redis_key('clean', project_id)
        p_state = redis_get_json(redis_key)
        if p_state and p_state.get('state') == AlgorithmState.ONGOING:
            # 传入的是TaskDbAlgorithm的DI
            query = TaskDbAlgorithm.objects.filter(id=db_algorithm_id).first()
            print('db_algorithm_id: ', db_algorithm_id, ' query:', query.id, 'result:', dialogue)
            if query:
                query.algorithm = dialogue
                query.state = 2
                query.remarks = ''
                query.save(update_fields=['algorithm', 'state', 'remarks'])
            count = TaskDbAlgorithm.objects.filter(
                project_id=project_id).filter(~Q(algorithm='')).count()
            redis_update_finish_state(redis_key, p_state, count=count)
    except Exception as e:
        TaskDbAlgorithm.objects.filter(task_id=db_algorithm_id).update(
            state=3, remarks=str(e)
        )


def insert_train_model(algorithm_result, model_train_id):
    # port = algorithm_result.get('port')
    print('result :::::', algorithm_result, ' train_id: ', model_train_id)
    port = algorithm_result
    if not port:
        logger.error('训练模型未返回端口')
    train = ModelTrain.objects.filter(id=model_train_id).first()
    if train.category != 'train':
        logger.error(f'训练记录类型错误，train id :{model_train_id}')
        return

    new_model = train.new_model
    if not new_model:
        print('model train id is :', model_train_id, ' Not new_model.')
        return
    if ':' in new_model.url:
        domain = ':'.join(new_model.url.split(':')[:-1])
        new_model.url = f'{domain}:{port}'
        new_model.state = 4
        new_model.save()
        train.state = 4
        train.train_finished_at = datetime.datetime.now()
        train.save()
    else:
        print('Model url is invalid. model id :', new_model.id)
