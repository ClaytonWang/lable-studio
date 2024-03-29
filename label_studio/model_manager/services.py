#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : services.py
  > CreateTime : 2022/7/24 09:26
"""
import os
import sys
import logging
import requests
from datetime import datetime, timezone
from django.conf import settings
from model_manager.models import ModelManager
logger = logging.getLogger('db')


def ml_backend_params(
        data, labels=[], templates=[], extra={}
):
    extra.update(**dict(
        labels={index: label for index, label in enumerate(labels)},
        templates=templates,
    ))
    return dict(
        data=data,
        extra=extra
    )


def ml_backend_request(
        uri: str, version='v3', method: str = 'get',
        params={}, data={}, _json={}
):
    """
    算法参数：
        {
            'labels':{0: '套餐', 1: '语音', 2: '流量', 3: '办理', 4: '否定', 5: '默认',  6: '肯定', 7: '不办理', 8: '返回主屏幕'}
            'templates': ['[dlg]请生成[lb]相关回复', '[dlg]你可以咨询[lb]相关问题']
            'return_nums': 3,
            'data':[
                {
                    'task_id': 450,
                    'dialogue': [
                       {'text': '好的，请问您还有其他业务需要办理吗？', 'author': 'a'},
                       {'text': '查套餐.查语音.查流量？', 'author': 'b'},
                       {'text': '正在为您办理XXX业务，业务套餐为XXX元xxx分钟包含XX兆流量', 'author': 'a'},
                       {'text': '您的XXX业务办理成功，请问您还有其他业务需要办理查询吗', 'author': 'b'},
                    ]
                }
            ]
        }
    算法返回：
        {
            "status": 0,
            "errorInfo": "",
            "data": {
                "download": url
            }
        }

    :param host:
    :param uri:
    :param version:
    :param method:
    :param params:
    :param data:
    :param _json:
    :return:
    """
    ml_url = os.path.join(settings.MODEL_SERVING_HOST, version, uri)
    logger.info(f'ML Request url:, {ml_url} {method} \nparams: {params}\ndata:{data}\njson:{_json}')
    session = getattr(requests, method)
    # ml_url = 'http://127.0.0.1:5000/api/v1/train'
    # print(_json['extra']['labels'])
    try:
        response = session(url=ml_url, params=params, data=data, json=_json)
    except Exception as e:
        return False, str(e)
    if response.status_code == 200:
        rsp_data = response.json()
        logger.info('ML response: ', rsp_data)
        rsp_state = rsp_data.get('status')
        if rsp_state == 0:
            return True, rsp_data.get('data', '')
        else:
            return False, rsp_data.get('errorInfo')
    else:
        return False, response.text


_true_set = {'yes', 'true', 't', 'y', '1'}
_false_set = {'no', 'false', 'f', 'n', '0'}


def str2bool(value, raise_exc=False):
    if isinstance(value, str):
        value = value.lower()
        if value in _true_set:
            return True
        if value in _false_set:
            return False

    if raise_exc:
        raise ValueError('Expected "%s"' % '", "'.join(_true_set | _false_set))
    return None


def check_model_state():
    """
    检查模型状态是否有进行中的状态，有并且启动时间超过12小时，把状态置成失败
    (3, '训练中'),
    (4, '已完成'),
    (5, '失败'),
    (6, '运行中'),
    """

    running = ModelManager.objects.filter(state__in=(3, 6)).all()
    for item in running:
        interval = datetime.now(timezone.utc) - item.created_at
        if interval.days >= 1:
            item.state = 5
            item.save()
