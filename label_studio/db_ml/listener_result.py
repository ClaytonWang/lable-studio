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
import time
import random
import string
from threading import Thread
from tasks.models import Task
from tasks.models import Prediction
from tasks.models import TaskDbAlgorithm
from projects.models import PromptResult
from db_ml.services import update_prediction_data
from db_ml.services import train_failure_delete_train_model
from model_manager.models import ModelTrain, ModelManager
from model_manager.services import ml_backend_request
from core.redis import _redis, redis_get, redis_delete, redis_healthcheck
logger = logging.getLogger('db')
DEFAULT_INTERRUPT_TIME = 5 * 60
DEFAULT_SLEEP_TIME = 0.5
CELERY_FINISH_STATUS = ('SUCCESS', 'FAILURE')

"""


"""


def thread_read_redis_celery_result(project_id, algorithm_type: str, record: ModelTrain):
    """
    触发调用算法，获取celery的结果线程，当前答案超过30分钟，自动结束线程
    :return:
    """

    Thread(target=read_redis_data, args=(project_id, algorithm_type, record)).start()


def read_redis_data(project_id, algorithm_type, record: ModelTrain):
    """
    每次循环默认间隔的时间是2秒

    最后一次获取成功数据到下一次获取的间隔超过5分钟，设置失败。
    :param project_id:
    :param algorithm_type:
    :param record: 模型执行记录对象
    :return:
    """
    last_success_time = time.time()

    while True:
        time.sleep(DEFAULT_SLEEP_TIME)
        record = ModelTrain.objects.filter(id=record.id).first()
        # 查询状态失败，退出
        if record.state == 5:
            break

        # 超时处理
        if int(time.time() - last_success_time) > DEFAULT_INTERRUPT_TIME or not record:
            print(f"ML {project_id}  {algorithm_type} timeout.")
            finsh, total = statistics_finish_count(algorithm_type, project_id)
            # TODO 添加空数据
            # 先测试没有加空值的影响，如果不影响整体流程，暂不处理
            if round(finsh/total, 2) < 0.8:
                record.state = 5  # 失败
            else:
                record.state = 4  # 成功
            record.save()
            break

        if algorithm_type == 'train':
            fuzzy_key = f'celery-task-meta*_{algorithm_type}_*'
        else:
            fuzzy_key = f'celery-task-meta*_{algorithm_type}_{record.id}*'
        if not redis_healthcheck():
            print('Redis is disconnect')
            return

        for key in _redis.scan_iter(fuzzy_key):
            status = None
            try:
                key = key.decode('utf-8')
                k_result = redis_get(key)
                k_result = json.loads(str(k_result, 'utf-8'))
                status = k_result.get('status')
                result = k_result.get('result', '')
                if status not in CELERY_FINISH_STATUS:
                    continue

                # 算法失败的结果为空，插入数据的值为空。保留一条空数据
                data = dict(
                    celery_task_id=key,
                    status=status,
                    result=result if status == 'SUCCESS' else '',
                    model_id=record.model.id if record.model else '',
                    record=record,
                    traceback=k_result.get('traceback', ''),
                )
                print('ML message. status: ', status, ' results:',  data)
                process_callback_result(data)
            except Exception as e:
                print(f'ML Exception: {e} celery_task_id {key}')
            finally:
                if status in CELERY_FINISH_STATUS:
                    last_success_time = time.time()
                    redis_delete(key)

        # 收集结束，退出循环
        finish, total = statistics_finish_count(algorithm_type, project_id)
        print('finish:', finish, '   total:', total)
        if finish == total:
            if algorithm_type != 'train':
                record.state = 4  # 成功
                record.save()
            break


def cancel_job_delete_redis_key(algorithm_type, record_id):
    if algorithm_type == 'train':
        fuzzy_key = f'celery-task-meta*_{algorithm_type}_*'
    else:
        fuzzy_key = f'celery-task-meta*_{algorithm_type}_{record_id}*'
    if not redis_healthcheck():
        print('Redis is disconnect')
        return

    for key in _redis.scan_iter(fuzzy_key):
        redis_delete(key)


def statistics_finish_count(algorithm_type, project_id) -> tuple:
    """
    统计结束的任务数 返回（已经结束，总数）
    """
    task_query = Task.objects.filter(project_id=project_id)
    finish_task = 0
    total_task = task_query.count()
    if algorithm_type == 'prediction':
        finish_task = Prediction.objects.filter(
            task__in=task_query
        ).count()
    elif algorithm_type == 'clean':
        clean_task_query = TaskDbAlgorithm.objects.filter(
            project_id=project_id
        )
        success_query = clean_task_query.filter(state=2)
        failed_query = clean_task_query.filter(state=3)
        finish_task = success_query.count() + failed_query.count()
    elif algorithm_type == 'prompt':
        finish_task = PromptResult.objects.filter(
            project_id=project_id
        ).count()
    elif algorithm_type == 'train':
        _train = ModelTrain.objects.filter(project_id=project_id).order_by('-id').first()
        # 训练模型已经完成，直接返回成功
        if _train and _train.category == 'train' and _train.state in (4, 5):
            finish_task = total_task

    return finish_task, total_task


def process_callback_result(data):
    model_id = data.get('model_id')
    task_status = data.get('status')
    celery_task_id = data.get('celery_task_id')
    result = data.get('result')

    algorithm_type, record_id, task_id = split_project_and_task_id(celery_task_id)
    print(' algorithm_type: ', algorithm_type, ' project_id: ', record_id, ' task_id: ', task_id)
    if algorithm_type == 'train' and task_status == 'FAILURE':
        train_failure_delete_train_model(record_id, data.get('traceback'))
        print(f'ML Train Task status is failed. {celery_task_id}')
    else:
        process_algorithm_result(algorithm_type, record_id, task_id, result, model_id)


def process_algorithm_result(algorithm_type, record_id, task_id, algorithm_result, model_id):
    """

    :param algorithm_type:
    :param record_id:
    :param task_id:
    :param algorithm_result:
    :param model_id:
    :return:
    """
    project = ModelTrain.objects.filter(id=record_id).first().project
    if not project:
        logger.info(f'Invalid record id : {record_id}')
        return
    project_id = project.id

    if algorithm_type == 'train':
        #
        """
        train 时，project_id带的是modelTrain的主键
         {port: 100010}
        """
        insert_train_model(algorithm_result, record_id)
    else:
        # project = Project.objects.filter(id=project_id).first()

        # 清洗算法结果入库
        if algorithm_type == 'clean':
            insert_clean_value(algorithm_result, project_id, task_id)
            return

        if project.template_type == 'intent-classification':
            if algorithm_type == 'prediction':
                data = get_prediction_intent_df(algorithm_result, task_id, model_id)
                insert_prediction_value(data, task_id)
            elif algorithm_type == 'prompt':
                insert_prompt_intent_value(algorithm_result, project_id, task_id, model_id)
        elif project.template_type == 'conversational-generation':
            if algorithm_type == 'prediction':
                data = get_prediction_generate_df(algorithm_result, task_id, model_id)
                insert_prediction_value(data, task_id)
            elif algorithm_type == 'prompt':
                insert_prompt_generate_value(algorithm_result, project_id, task_id, model_id)
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


def insert_prediction_value(data, task_id):
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

    :param task_id:
    :param data:
    :return:
    """
    tag_data = data
    print(f"results: ....{str(tag_data)}")
    obj, is_created = Prediction.objects.update_or_create(
        defaults=tag_data, task_id=task_id
    )
    print('obj:', obj.id, ' is_ created:', is_created)


def get_prediction_intent_df(algorithm_result, task_id, model_id=None):
    annotation, confidence = (algorithm_result[0], algorithm_result[1]) if algorithm_result else ('', 0)
    pre_result = {
        'id': ''.join(random.sample(string.ascii_lowercase + string.ascii_uppercase, 10)),
        'origin': 'prediction',
        'from_name': 'intent',
        'to_name': 'dialogue',
        'type': 'choices',
        'value': {
            'choices': [annotation], 'start': 0, 'end': 1
        },
    }
    tag_data = dict(
        model_id=model_id,
        task_id=task_id,
        result=[pre_result],
        score=round(confidence, 4),

    )
    return tag_data


def conversation_generation_save_template(
        value_text: list, origin='prediction',
        from_name: str = 'response'
) -> dict:
    """
    拼接对话生成的保存数据结构
    :param from_name:
    :param value_text:
    :param origin:
    :return:
    """
    result = {
        'id': ''.join(random.sample(string.ascii_lowercase + string.ascii_uppercase, 10)),
        'origin': origin,
        'from_name': from_name,
        'to_name': 'chat',
        "type": "textarea",
        'value': {
            "text": value_text if isinstance(value_text, list) else [value_text],
        },
    }
    return result


def join_text(_result):
    text = []
    for sub_text in _result:
        for _text in sub_text:
            text.append(_text)
    return text


def get_prediction_generate_df(algorithm_result, task_id, model_id=None):
    """
    对话生成的入库数据格式：

    对话生成算法返回结果

    统一返回的算法结果20221025号前的返回结构
    ['我要升级套餐', '哦，我挂了']

    不同标签对应的算法返回结果
    {'标签', []}
    {'升级', ['我要升级套餐', '哦，我挂了']}

    :param algorithm_result:
    :param task_id:
    :param model_id:
    :return:
    """
    pre_result = []
    if isinstance(algorithm_result, dict):
        for from_name, res in algorithm_result.items():
            _item_res = conversation_generation_save_template(res, 'prediction', from_name)
            pre_result.append(_item_res)
    else:
        # 标签和对话不需要映射的入库
        pre_result = conversation_generation_save_template(join_text(algorithm_result), 'prediction', 'response')
    tag_data = dict(
        model_id=model_id,
        task_id=task_id,
        result=pre_result,
    )
    return tag_data


def insert_prompt_intent_value(algorithm_result, project_id, task_id, model_id=None):
    """
    预标注 0样本
    :param algorithm_result:
    :param project_id:
    :param task_id:
    :param model_id:
    :return:
    """
    # annotation, confidence = (algorithm_result[0], algorithm_result[1]) if algorithm_result else ('', 0)
    annotation, confidence = (algorithm_result[0][0], 0) if algorithm_result else ('', 0)
    result = {
        "task": '',
        "annotation": annotation,
        "confidence": confidence,
        "average": '',
        "output": []
    }

    update_prediction_data(task_id, result, model_id=model_id)
    obj = PromptResult(project_id=project_id, task_id=task_id, metrics=result)
    obj.save()


def insert_prompt_generate_value(algorithm_result, project_id, task_id, model_id=None):
    """
    对话生成 0样本
    :param algorithm_result:
    :param project_id:
    :param task_id:
    :param model_id:
    :return:
    """

    pre_result = []
    if isinstance(algorithm_result, dict):
        for from_name, res in algorithm_result.items():
            _res = join_text(res)
            _item_res = conversation_generation_save_template(_res, 'prediction', from_name)
            pre_result.append(_item_res)
    else:
        # 标签和对话不需要映射的入库
        pre_result = conversation_generation_save_template(
            join_text(algorithm_result), 'prediction', 'response'
        )

    tag_data = dict(model_id=model_id, task_id=task_id, result=pre_result)
    a, is_created = Prediction.objects.update_or_create(
        defaults=tag_data, task_id=task_id
    )
    print(f'prompt Prediction result: {a} {is_created}')

    obj = PromptResult(project_id=project_id, task_id=task_id, metrics=algorithm_result)
    obj.save()


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
        # 传入的是TaskDbAlgorithm的DI
        query = TaskDbAlgorithm.objects.filter(id=db_algorithm_id).first()
        print('db_algorithm_id: ', db_algorithm_id, ' query:', query.id, 'result:', dialogue)
        if query:
            query.algorithm = dialogue
            query.state = 2
            query.remarks = ''
            query.save(update_fields=['algorithm', 'state', 'remarks'])
    except Exception as e:
        TaskDbAlgorithm.objects.filter(task_id=db_algorithm_id).update(
            state=3, remarks=str(e)
        )


def insert_train_model(algorithm_result, model_train_id):
    # port = algorithm_result.get('port')
    print('result :::::', algorithm_result, ' train_id: ', model_train_id)
    # TODO 训练结果返回，返回模型标签
    train = ModelTrain.objects.filter(id=model_train_id).first()
    if train.category != 'train':
        logger.error(f'训练记录类型错误，train id :{model_train_id}')
        return

    new_model = train.new_model
    if not new_model:
        print('model train id is :', model_train_id, ' Not new_model.')
        return

    new_model.state = 4
    new_model.save()

    train.state = 4
    train.train_finished_at = datetime.datetime.now()
    # train.train_finished_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    train.save()

    time.sleep(2)
    state, rsp = ml_backend_request(
        uri='getLabels', method='get',
        params=dict(hash_id=new_model.hash_id)
    )
    if state:
        labels = rsp.values()
        new_model.labels = ','.join(labels)
        new_model.save()
