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
from tasks.models import Task
from tasks.models import TaskDbTag


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

    if TaskDbTag.objects.filter(project_id=project_id).exists():
        TaskDbTag.objects.filter(project_id=project_id).delete()

    for item in query:
        # TODO 多对话判断
        text = item.data.get('dialogue')[0].get('text')
        data = dict(
            text=text,
            project_id=project_id,
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
    total_task = Task.objects.filter(project_id=project_id).count()
    pre_task = TaskDbTag.objects.filter(project_id=project_id).count()
    return Response(data=dict(
        total=total_task,
        finish=pre_task,
        rate=round(pre_task/total_task, 2) if total_task > 0 else 0
    ))
