#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : api.py
  > CreateTime : 2022/6/7 15:29
"""
import json
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
from tasks.models import Task
from tasks.models import Prediction, PredictionDraft
from tasks.models import TaskDbAlgorithm, TaskDbAlgorithmDraft
from projects.models import PromptResult, PromptTemplates, Project
from db_ml.services import PREDICTION_BACKUP_FIELDS
from db_ml.services import CLEAN_ALGORITHM_BACKUP_FIELDS
from db_ml.services import rollback_prediction
from db_ml.services import rollback_clean
from db_ml.services import rollback_prompt
from db_ml.services import save_raw_data
from db_ml.services import generate_redis_key
from db_ml.services import AlgorithmState
from db_ml.services import redis_set_json, redis_get_json
from db_ml.services import predict_prompt
from db_ml.services import preprocess_clean
from db_ml.services import generate_uuid
from db_ml.services import get_project_labels
from db_ml.services import cut_task_to_model
from db_ml.services import query_last_record
from db_ml.services import create_model_record
from db_ml.listener_result import cancel_job_delete_redis_key
from db_ml.listener_result import thread_read_redis_celery_result
from model_manager.models import ModelTrain, ModelManager
from model_manager.serializers_train import ModelTrainDetailSerializer
from projects.services import get_template
from tasks.tag_services import created_clean_base_data


logger = logging.getLogger('db')

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
    model_ids = data.get('model_ids', '').split(',')
    model_ids = [int(item) for item in model_ids if item]
    clean_query = TaskDbAlgorithm.objects.filter(project_id=project_id)
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return Response(data=dict(msg='Invalid project id'))
    if not clean_query:
        tasks = Task.objects.filter(project_id=project_id).all()
        created_clean_base_data(tasks, project_id, request.user.id)

    if query_last_record(project_id):
        return Response(status=400, data=dict(msg='Project is running model.'))

    # 备份一份原数据后删除原记录
    if TaskDbAlgorithmDraft.objects.filter(project_id=project_id).exists():
        TaskDbAlgorithmDraft.objects.filter(project_id=project_id).delete()

    first_model_id = model_ids[0]
    remark = ','.join([str(i) for i in model_ids])
    record_status, record = create_model_record(
        first_model_id, project_id, request.user, remark=remark
    )
    if not record_status:
        return Response(status=400, data=dict(msg='Invalid model id.'))

    _uuid = generate_uuid('clean', record.id)

    with atomic():
        query_alg = TaskDbAlgorithm.objects.filter(project_id=project_id).all()
        if len(query_alg):
            save_raw_data(
                query_alg, TaskDbAlgorithmDraft, CLEAN_ALGORITHM_BACKUP_FIELDS
            )
            TaskDbAlgorithm.objects.filter(project_id=project_id).update(
                algorithm='',
                state=1,
            )

        for sub_query in cut_task_to_model(clean_query):
            task_data = []
            for item in sub_query:
                dialogue = item.source
                task_data.append(dict(
                    task_id=item.id,
                    dialogue=dialogue
                ))
            state, result = preprocess_clean(
                project_id, model_ids, task_data, _uuid
            )
            if not state:
                record.state = 5
                record.save()
                return Response(status=status.HTTP_400_BAD_REQUEST, data=dict(message=result))

        thread_read_redis_celery_result(project_id, 'clean', record)
    return Response(data=dict(msg='Submit success', project_id=project_id, record=record.id))


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
        project_id=project_id,
        # state=2  # 不限制状态
    )
    if not query:
        return Response(status=400, data=dict(msg=f'项目ID{project_id}没有查询到清洗数据'))

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prediction(request):
    """
    :param request:
    :return:
    """
    data = request.data
    project_id = data.get('project_id')
    model_id = data.get('model_id', '')
    query = Task.objects.filter(project_id=project_id)

    if not query:
        return Response(status=400, data=dict(msg='Invalid project id'))

    if query_last_record(project_id):
        # TODO 如纪录的时间已经很长，需要手动设置失效状态
        return Response(status=400, data=dict(msg='项目有正在运行的模型'))

    project = query.first().project
    # # 生成对话普通 取消模型选择(没有模型选择，后端自动添加模型 普通模型)，
    if project.template_type == 'conversational-generation' and not model_id:
        model = ModelManager.objects.filter(type='dialogue', version='1.0', base=True).first()
        model_id = model.id

    # 创建模型调用记录
    record_status, record = create_model_record(model_id, project_id, request.user)
    if not record_status:
        return Response(status=400, data=dict(msg='Invalid model id.'))

    task_ids = [item.id for item in query]
    if PredictionDraft.objects.filter(task_id__in=task_ids).exists():
        PredictionDraft.objects.filter(task_id__in=task_ids).delete()

    # 因使用模型调用记录，原来project id改成记录的ID，project id通过模型记录获取
    _uuid = generate_uuid('prediction', record.id)
    # 备份一份原数据后删除原记录
    with atomic():
        query_pre = Prediction.objects.filter(task_id__in=task_ids).all()
        if len(query_pre):
            save_raw_data(query_pre, PredictionDraft, PREDICTION_BACKUP_FIELDS)
            query_pre.delete()
            # Prediction.objects.filter(task_id__in=task_ids).delete()

        # 异常的信息回滚
        labels = get_project_labels(project_id)
        for sub_query in cut_task_to_model(query):
            task_data = []
            for item in sub_query:
                dialogue = item.data.get('dialogue', [])
                task_data.append(dict(
                    task_id=item.id,
                    dialogue=dialogue
                ))

            state, result = None, None
            if project.template_type == 'intent-classification':
                # 意图标注
                state, result = predict_prompt(
                   project_id, model_id, task_data, _uuid
                )
            elif project.template_type == 'conversational-generation':
                # 对话生产
                if len(labels):
                    generate_count = data.get('generate_count')
                    templates = get_template(project_id)
                    state, result = predict_prompt(
                        project_id, model_id, task_data, _uuid,
                        return_num=generate_count, template=templates
                    )
                else:
                    state = False
                    result = '项目未设置标签'

            if not state:
                record.state = 5
                record.save()
                return Response(status=400, data=dict(message=result))

        thread_read_redis_celery_result(project_id, 'prediction', record)
    return Response(data=dict(
        msg='Submit success', project_id=project_id, record_id=record.id
    ))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_task(request):
    """
    查询任务计算状态
    prediction - 预标注
    prompt     - 提示学习
    clean      - 清洗
    algorithm_type
    :param request:
    :return:
    """
    data = request.GET.dict()
    project_id = data.get('project_id')
    algorithm_type = data.get('type')
    category = data.get('category', 'model')

    # 查询redis的结果信息
    # 10/26 修改获取结果逻辑, 单独通过线程获取
    # read_redis_data(project_id, algorithm_type)

    query = Task.objects.filter(project_id=project_id)
    total_task = query.count()
    task_ids = [item.id for item in query]
    state = False

    # 状态从redis改成数据库记录
    record = ModelTrain.objects.filter(project_id=project_id, category=category)
    if algorithm_type == 'prediction':
        record = record.filter(model__type__in=['annotation', 'dialogue'], model__title__icontains='普通')
    elif algorithm_type == 'prompt':
        record = record.filter(model__type__in=['intention', 'dialogue_prompt'], model__title__icontains='0样本')
    elif algorithm_type == 'clean':
        record = record.filter(model__type__in=['bart_for_turn', 'intelligent', 'rule'])

    record = record.order_by('-id').first()
    if not record:
        return Response(data=dict(total=total_task, finish=0, state=5, rate=1))

    finish_task = 0
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
        finish_task = success_query.count() + failed_query.count()
        if clean_task_query.filter(state=1).count():
            state = True
    elif algorithm_type == 'prompt':
        # total_task = PromptTemplates.objects.filter(
        #     project_id=project_id
        # ).count() * total_task
        finish_task = PromptResult.objects.filter(
            project_id=project_id
        ).count()
        if 0 < finish_task < total_task:
            state = True

    if algorithm_type == 'train':
        train_data = ModelTrainDetailSerializer(record).data
        rate = train_data.get('training_progress', 1)
    else:
        rate = round(finish_task / total_task, 2) if total_task > 0 else 0

    return Response(data=dict(
        total=total_task,
        finish=finish_task,
        # true 是进行中  false是结束或未开始
        # state=state if int(rate) != 1 else False,
        state=record.state,  # (3, '训练'), (4, '完成'), (5, '失败'), (6, '运行中'),
        rate=rate
    ))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_job(request):
    """
    # TODO  修改取消逻辑
    :param request:
    :return:
    """
    data = request.GET.dict()
    project_id = data.get('project_id')
    algorithm_type = data.get('type')
    if algorithm_type not in ('prediction', 'clean', 'prompt') or not project_id:
        return Response(status=400, data=dict(error='Type/Project Error.'))

    record = ModelTrain.objects.filter(
        project_id=project_id, category='model', state=6  # 运行中
    ).order_by('-id').first()

    if not record:
        return Response(status=400, data=dict(msg="没有查询到模型运行记录"))

    record.state = 5
    record.save()
    # 删除redis没有执行的任务数据
    cancel_job_delete_redis_key(algorithm_type, record.id)

    if algorithm_type == 'prediction':
        rollback_prediction(project_id)
    elif algorithm_type == 'clean':
        rollback_clean(project_id)
    elif algorithm_type == 'prompt':
        rollback_prompt(project_id)

    return Response(data=dict(msg='cancel successfully'))
