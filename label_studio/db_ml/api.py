#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api.py
  > CreateTime : 2022/6/7 15:29
"""
import time
import logging
from django.db import connection
from django.db.models import Count
from datetime import datetime, timedelta
from django.db.models import Q
from django_rq.queues import get_queue
from rest_framework import status
from django.db.transaction import atomic
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from core.redis import start_job_async_or_sync
from core.redis import redis_set, redis_get
from db_ml.predict import job_predict
from db_ml.clean import job_clean
from tasks.models import Task
from tasks.models import Prediction, PredictionDraft
from tasks.models import TaskDbAlgorithm, TaskDbAlgorithmDraft
from projects.models import PromptResult, PromptTemplates
from db_ml.services import PREDICTION_BACKUP_FIELDS
from db_ml.services import CLEAN_ALGORITHM_BACKUP_FIELDS
from db_ml.services import rollback_prediction
from db_ml.services import rollback_clean
from db_ml.services import rollback_prompt
from db_ml.services import save_raw_data
from db_ml.services import generate_redis_key
from db_ml.services import AlgorithmState
from db_ml.services import redis_set_json, redis_get_json
from model_manager.services import ml_backend_request


"""
项目执行算法状态标识

前缀 DB_ALGORITHM_{算法名称}_{项目ID} 

状态：
state = dict(
    init='初始化',
    ongoing='执行中',
    finish='执行结束',
    cancel='取消'
)

"""


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clean(request):
    """
    调用清洗算法
    :param request:
    :return:
    """
    data = request.data
    project_id = data.get('project_id')
    query = TaskDbAlgorithm.objects.filter(project_id=project_id)
    if not query:
        return Response(data=dict(msg='Invalid project id'))

    redis_key = generate_redis_key('clean', str(project_id))
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data=dict(msg='Project is running clean.')
        )

    # 备份一份原数据后删除原记录
    if TaskDbAlgorithmDraft.objects.filter(project_id=project_id).exists():
        TaskDbAlgorithmDraft.objects.filter(project_id=project_id).delete()

    redis_state = dict(
        state=AlgorithmState.ONGOING,
        total=query.count(),
        project_id=project_id,
        username=request.user.username,
    )
    redis_set_json(redis_key, redis_state)
    with atomic():
        query_alg = TaskDbAlgorithm.objects.filter(project_id=project_id).all()
        if len(query_alg):
            save_raw_data(
                query_alg, TaskDbAlgorithmDraft, CLEAN_ALGORITHM_BACKUP_FIELDS
            )
            TaskDbAlgorithm.objects.filter(project_id=project_id).update(
                algorithm='',
                manual='',
                state=1,
            )

        for item in query:
            dialog = item.source
            data = dict(
                project_id=project_id,
                task_id=item.task.id,
                user_id=request.user.id,
                algorithm_id=item.id,
                queue_name='algorithm_clean',
                dialog=dialog,
            )
            start_job_async_or_sync(job_clean, **data)
            # job_clean(**data)
    return Response(data=dict(msg='Submit success', project_id=project_id))


@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def replace(request):
    """
    手工替换数据
    清洗-替换数据
    :param request:
    :return:
    """
    data = request.data
    project_id = data.get('project_id')
    query = TaskDbAlgorithm.objects.filter(
        project_id=project_id, state=2
    )
    if not query:
        return Response(data=dict(msg='Invalid project id'))

    for item in query:
        if item.manual:
            item.task.data = dict(dialogue=item.manual)
            item.task.save()
            continue
        elif item.algorithm:
            item.task.data = dict(dialogue=item.algorithm)
            item.task.save()
            continue

    return Response(data=dict(msg='Replace finished', project_id=project_id))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_clean_task(request):
    data = request.GET.dict()
    project_id = data.get('project_id')

    clean_task_query = TaskDbAlgorithm.objects.filter(
        project_id=project_id
    )
    total = clean_task_query.count()
    success_query = clean_task_query.filter(state=2)
    failed_query = clean_task_query.filter(state=3)
    #     clean_task_query.filter(
    #     Q(~Q(algorithm= '')) | Q(algorithm__isnull=True)
    # )
    success_count = success_query.count()
    failed_count = failed_query.count()
    finish = success_count + failed_count
    return Response(data=dict(
        total=total,
        finish=finish,
        falied=failed_count,
        success=success_count,
        state=True if clean_task_query.filter(state=1).count() else False,
        rate=round(finish / total, 2) if total > 0 else 0
    ))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prediction(request):
    """
    :param request:
    :return:
    """
    data = request.data
    project_id = data.get('project_id')
    redis_key = generate_redis_key('prediction', str(project_id))
    query = Task.objects.filter(project_id=project_id)
    if not query:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data=dict(msg='Invalid project id')
        )
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data=dict(msg='Project is running prediction.')
        )

    task_ids = [item.id for item in query]
    if PredictionDraft.objects.filter(task_id__in=task_ids).exists():
        PredictionDraft.objects.filter(task_id__in=task_ids).delete()

    redis_state = dict(
        state=AlgorithmState.ONGOING,
        total=query.count(),
        project_id=project_id,
        username=request.user.username,
    )
    redis_set_json(redis_key, redis_state)
    # 备份一份原数据后删除原记录
    with atomic():
        query_pre = Prediction.objects.filter(task_id__in=task_ids).all()
        if len(query_pre):
            save_raw_data(query_pre, PredictionDraft, PREDICTION_BACKUP_FIELDS)
            query_pre.delete()
            # Prediction.objects.filter(task_id__in=task_ids).delete()

        # TODO 多对话判断
        # 异常的信息回滚
        for item in query:
            # text = item.data.get('dialogue')[0].get('text')
            text = item.data.get('dialogue', [])
            data = dict(
                text=text,
                project_id=project_id,
                task_id=item.id,
                task_tag_id=item.id,
                user_id=request.user.id,
                queue_name='prediction',
            )
            # 接模型服务接口
            # /api/ml_backend/predict?orginzation=orginzation&user=user
            # job = start_job_async_or_sync(job_predict, **data)
    return Response(data=dict(msg='Submit success', project_id=project_id))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_task(request):
    data = request.GET.dict()
    project_id = data.get('project_id')
    algorithm_type = data.get('type')

    query = Task.objects.filter(project_id=project_id)
    total_task = query.count()
    task_ids = [item.id for item in query]
    state = False

    redis_key = generate_redis_key(algorithm_type, str(project_id))
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        state = True
        finish = p_state.get('finish', 0)
        total = p_state.get('total', 0)
        return Response(data=dict(
            total=total,
            finish=finish,
            # true 是进行中  false是结束或未开始
            state=state if finish != total or \
                           state == AlgorithmState.ONGOING else False,
            rate=round(finish / total, 2) if total > 0 else 0
        ))

    if algorithm_type == 'prediction':
        finish_task = Prediction.objects.filter(
            task_id__in=task_ids
        ).count()
        print('count:', finish_task)
        if 0 < finish_task < total_task:
            state = True
    elif algorithm_type == 'clean':
        clean_task_query = TaskDbAlgorithm.objects.filter(
            project_id=project_id
        )
        total = clean_task_query.count()
        success_query = clean_task_query.filter(state=2)
        failed_query = clean_task_query.filter(state=3)
        success_count = success_query.count()
        failed_count = failed_query.count()
        finish_task = success_count + failed_count
        if clean_task_query.filter(state=1).count():
            state = True
    elif algorithm_type == 'prompt':
        total_task = PromptTemplates.objects.filter(
            project_id=project_id
        ).count() * total_task
        finish_task = PromptResult.objects.filter(
            project_id=project_id
        ).count()
        if 0 < finish_task < total_task:
            state = True
    else:
        return Response(dict(rate=0, state=False))

    return Response(data=dict(
        total=total_task,
        finish=finish_task,
        # true 是进行中  false是结束或未开始
        state=state,
        rate=round(finish_task / total_task, 2) if total_task > 0 else 0
    ))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_job(request):
    data = request.GET.dict()
    project_id = data.get('project_id')
    algorithm_type = data.get('type')
    if algorithm_type not in ('prediction', 'clean', 'prompt') or not project_id:
        return Response(status=400, data=dict(error='Type/Project Error.'))

    queue_mapping = dict(
        prediction='prediction',
        clean='algorithm_clean',
        prompt='prompt',
    )

    queue_name = queue_mapping[algorithm_type]
    redis_key = generate_redis_key(algorithm_type, str(project_id))

    p_state = redis_get_json(redis_key)
    p_state['state'] = AlgorithmState.FAILED
    redis_set_json(redis_key, p_state)

    if algorithm_type == 'prediction':
        rollback_prediction(project_id)
    elif algorithm_type == 'clean':
        rollback_clean(project_id)
    elif algorithm_type == 'prompt':
        rollback_prompt(project_id)

    count = 0
    for job in get_queue(queue_name).jobs:
        if project_id != str(job.kwargs.get('project_id', -1)):
            continue
        count += 1
        job.delete()

    # if not count:
    #     return Response(
    #         status=400, data=f'End of task execution. Project Id:{project_id}'
    #     )
    return Response(data=dict(msg='cancel successfully'))
