#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : tag_services.py
  > CreateTime : 2022/6/15 14:52
"""
import logging
from tasks.models import TaskDbAlgorithm
from tasks.tag_serializers import TagCleanCreatedSerializer
logger = logging.getLogger('console')


def bulk_create_algorithm_clean(task_dialog: list):
    serializer = TagCleanCreatedSerializer(data=task_dialog, many=True)
    serializer.is_valid(raise_exception=True)
    clean_instances = serializer.save()
    print("*" * 20, len(clean_instances))
    logger.debug(f'Success insert count:{len(clean_instances)}')


def created_clean_base_data(tasks, project_id, user_id):
    clean_data = [dict(
        source=item.data.get('dialogue', []),
        project=project_id,
        task=item.id,
        created_by=user_id,
        # task_id=item.id,
        # project_id=self.kwargs['pk'],
        # created_by_id=request.user.id
    ) for item in tasks]
    bulk_create_algorithm_clean(clean_data)


def delete_algorithm_clean(task_ids: list):
    TaskDbAlgorithm.objects.filter(id__in=task_ids).delete()
