#!/usr/bin/env python
# encoding: utf-8

"""
  http://redisdoc.com/topic/notification.html
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : algorithm_result.py
  > CreateTime : 2022/8/4 08:27
"""
import time
import logging
import threading
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
CELERY STATE
PENDING  等待
STARTED  开始
SUCCESS  成功
FAILURE  失败
RETRY    重试
REVOKED  撤销

"""


class RedisSpaceListener(object):
    """
    """
    def __init__(self, redis, key_prefix='celery-task-meta-', db_index=0):
        """
        """
        self.redis = redis
        self._thread = None
        self.pubsub = self.redis.pubsub()
        # 订阅消息
        self.pubsub.psubscribe(f'__keyspace@{db_index}__:{key_prefix}*')

    def start(self):
        print('redis listen threading ....')
        self._thread = t = threading.Thread(target=self._monitor)
        t.setDaemon(False)
        t.start()

    def _monitor(self):
        """
        """
        while True:
            message = self.pubsub.get_message()
            if message:
                if message.get('type') != 'pmessage':
                    continue
                key = str(message.get('channel', b''), 'utf-8')
                print(key)
            else:
                time.sleep(0.1)

    def stop(self):
        self._thread.join()
        self._thread = None


def process_celery_result(key):
    k_result = redis_get(key)
    # 状态判断 不符合处理的状态丢弃

    celery_task_id = k_result.get('task_id')
    algorithm_type, project_id, task_id = split_project_and_task_id(
        celery_task_id
    )

    algorithm_result = k_result.get('result')
    if algorithm_type == 'prediction':
        insert_prediction_value(algorithm_result, project_id, task_id)
        pass
    elif algorithm_type == 'prompt':
        pass
    elif algorithm_type == 'clean':
        pass
    else:
        logger.info(f'Invalid algorithm_type: {algorithm_type}')


def split_project_and_task_id(celery_task_id) -> list:
    """
    celery-task-met-{_uuid}_{algorithm_type}_{project_id}_{task_id}'
    :param celery_task_id:
    :return:
    """
    algorithm_type, project_id, task_id = None, None, None
    try:
        _, algorithm_type, project_id, task_id = celery_task_id.split('-')
    except Exception as e:
        logger.warning(
            f'Redis receive celery id :{celery_task_id} \n exception msg:{e}'
        )
    return [algorithm_type, project_id, task_id]


def insert_prediction_value(algorithm_result, project_id, task_id):
    if not task_id or not project_id:
        logger.warning(
            f"Invalid project id or task id."
            f" project:{project_id} task:{task_id}"
        )
        return

    res_text, confidence = '', 0
    pre_result = {
        'origin': 'prediction',
        'from_name': 'intent',
        'to_name': 'dialogue',
        'type': 'choices',
        'value': {
            'choices': [res_text], 'start': 0, 'end': 1
        },
    }
    tag_data = dict(
        # project_id=kwargs.get('project_id'),
        task=task_id,
        result=[pre_result],
        score=round(confidence, 4),

    )
    print(f"results: ....{str(tag_data)}")
    redis_key = generate_redis_key('prediction', project_id)
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        obj, is_created = Prediction.objects.update_or_create(
            defaults=tag_data, task=task_id
        )
        redis_update_finish_state(redis_key, p_state)
        print('obj:', obj.id, ' auto: ', res_text, ' is_ created:',
              is_created)


def inset_prompt_value(algorithm_result, project_id, task_id):
    res_text, confidence = '', 0
    result = {
        "task": '',
        "annotation": res_text,
        "confidence": confidence,
        # "average": {"正面标签": np.random.rand(), "负面标签": np.random.rand()},
        # "output":
        #     [
        #         {"template": "你好，我是模版A1",
        #       "label": "正面",
        #       # "score": "烂片%f" % np.random.rand(),
        #       # "wgtedAvg": np.random.rand()
        #          },
        #      {
        #          "template": "你好，我是模版B",
        #       "label": "负面",
        #       "score": "精品%f" % np.random.rand(),
        #       "wgtedAvg": np.random.rand()}
        #      ]
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


def insert_clean_value(algorithm_result, project_id, algorithm_id):
    turn = algorithm_result.get('', [])
    try:
        # 拼接回对话模式
        result = []
        for item in turn:
            for k, v in item.items():
                result.append(dict(author=str(k), text=v))

        redis_key = generate_redis_key('clean', project_id)
        p_state = redis_get_json(redis_key)
        if p_state and p_state.get('state') == AlgorithmState.ONGOING:
            TaskDbAlgorithm.objects.filter(id=algorithm_id).update(
                algorithm=result, state=2, remarks=''
            )
            redis_update_finish_state(redis_key, p_state)
    except Exception as e:
        TaskDbAlgorithm.objects.filter(id=algorithm_id).update(
            state=3, remarks=str(e)
        )
