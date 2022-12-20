#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : services.py
  > CreateTime : 2022/7/24 09:26
"""
import os
import logging
import requests
from typing import Optional, List
from django.conf import settings
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
        uri: list, version='v3', method: str = 'get',
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
    ml_url = os.path.join(settings.MODEL_SERVING_HOST, version, *uri)
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
