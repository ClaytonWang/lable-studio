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


@api_view(['POST'])
@permission_classes([AllowAny])
def prediction(request):
    """
    :param request:
    :return:
    """
    from tasks.models import Task
    data = request.data
    project_id = data.get('project_id')
    query = Task.objects.filter(project_id=project_id)

    for item in query:
        text = item.data.get('dialogue')[0].get('text')
        data = dict(
            text=text,
            project_id=project_id,
            task_tag_id=item.id,
            user_id=request.user.id,
            queue_name='pre_tags',
        )
        start_job_async_or_sync(job_predict, **data)
        break
    else:
        return Response(data=dict(msg='Invalid project id'))

    return Response(data=dict(msg='Submit success'))
