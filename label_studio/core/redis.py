"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import time
import redis
import logging
import threading
import django_rq

from django_rq import get_connection

logger = logging.getLogger(__name__)

try:
    _redis = get_connection()
    _redis.ping()
    logger.info('=> Redis is connected successfully.')
except:
    logger.info('=> Redis is not connected.')
    _redis = None


def redis_listener():
    if redis_healthcheck():
        from db_ml.listener_result import RedisSpaceListener
        return RedisSpaceListener(_redis)
    else:
        logger.error('Redis connection failed...')


def redis_healthcheck():
    if not _redis:
        return False
    try:
        _redis.ping()
    except redis.exceptions.ConnectionError as exc:
        logger.error(f'Redis healthcheck failed with ConnectionError: {exc}', exc_info=True)
        return False
    except redis.exceptions.TimeoutError as exc:
        logger.error(f'Redis healthcheck failed with TimeoutError: {exc}', exc_info=True)
        return False
    except redis.exceptions.RedisError as exc:
        logger.error(f'Redis healthcheck failed: {exc}', exc_info=True)
        return False
    else:
        logger.info('Redis client is alive!')
        return True


def redis_connected():
    return redis_healthcheck()


def redis_get(key):
    if not redis_healthcheck():
        return
    return _redis.get(key)


def redis_hget(key1, key2):
    if not redis_healthcheck():
        return
    return _redis.hget(key1, key2)


def redis_set(key, value, ttl=None):
    if not redis_healthcheck():
        return
    return _redis.set(key, value, ex=ttl)


def redis_hset(key1, key2, value):
    if not redis_healthcheck():
        return
    return _redis.hset(key1, key2, value)


def redis_delete(key):
    if not redis_healthcheck():
        return
    return _redis.delete(key)


def start_job_async_or_sync(job, *args, **kwargs):
    """
    Start job async with redis or sync if redis is not connected
    :param job: Job function
    :param args: Function arguments
    :param kwargs: Function keywords arguments
    :return: Job or function result
    """
    redis = redis_connected()
    queue_name = kwargs.get("queue_name", "default")
    if 'queue_name' in kwargs:
        del kwargs['queue_name']
    if redis:
        queue = django_rq.get_queue(queue_name)
        job = queue.enqueue(
            job,
            *args,
            **kwargs
        )
        return job
    else:
        return job(*args, **kwargs)


class RedisSpaceListener(object):
    """
    """
    def __init__(self, _redis, key_prefix='celery-task-meta-', db_index=0):
        """
        """
        self.redis = _redis
        self._thread = None
        self.pubsub = None
        self.key_prefix = key_prefix
        self.db_index = db_index
        self.subscribe()

    def subscribe(self):
        self.pubsub = self.redis.pubsub()
        # 订阅消息
        self.pubsub.psubscribe(
            f'__keyspace@{self.db_index}__:{self.key_prefix}*'
        )

    def start(self):
        print('Redis listening thread ....')
        self._thread = t = threading.Thread(target=self._monitor)
        t.setDaemon(False)
        t.start()

    def _monitor(self):
        """
        """
        from db_ml.listener_result import process_celery_result
        while True:
            message = self.pubsub.get_message()
            if message:
                if message.get('type') != 'pmessage':
                    continue

                key = str(message.get('channel', b''), 'utf-8')
                process_celery_result(key)
            else:
                time.sleep(0.1)

    def stop(self):
        self._thread.join()
        self._thread = None
