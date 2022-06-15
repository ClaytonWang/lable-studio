#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api.py
  > CreateTime : 2022/6/7 15:29
"""
import logging
from django.db import connection
from django.db.models import Count
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from core.redis import start_job_async_or_sync
from db_ml.predict import job_predict
from db_ml.clean import job_clean
from tasks.models import Task
from tasks.models import Prediction
from tasks.models import TaskDbAlgorithm
from core.redis import redis_connected


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

    TaskDbAlgorithm.objects.filter(project_id=project_id).update(
        algorithm='',
        manual='',
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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def replace(request):
    """
    清洗-替换数据
    :param request:
    :return:
    """
    data = request.data
    project_id = data.get('project_id')
    query = TaskDbAlgorithm.objects.filter(project_id=project_id)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prediction(request):
    """
    :param request:
    :return:
    """
    data = request.data
    project_id = data.get('project_id')
    query = Task.objects.filter(project_id=project_id)
    if not query:
        return Response(data=dict(msg='Invalid project id'))

    task_ids = [item.id for item in query]
    if Prediction.objects.filter(task_id__in=task_ids).exists():
        Prediction.objects.filter(task_id__in=task_ids).delete()

    for item in query:
        # TODO 多对话判断
        text = item.data.get('dialogue')[0].get('text')
        data = dict(
            text=text,
            project_id=project_id,
            task_id=item.id,
            task_tag_id=item.id,
            user_id=request.user.id,
            queue_name='pre_tags',
        )
        start_job_async_or_sync(job_predict, **data)
    return Response(data=dict(msg='Submit success', project_id=project_id))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_task(request):
    data = request.GET.dict()
    project_id = data.get('project_id')

    query = Task.objects.filter(project_id=project_id)
    total_task = query.count()

    task_ids = [item.id for item in query]
    pre_task = Prediction.objects.filter(task_id__in=task_ids).count()
    return Response(data=dict(
        total=total_task,
        finish=pre_task,
        rate=round(pre_task/total_task, 2) if total_task > 0 else 0
    ))
