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
from django.conf import settings
logger = logging.getLogger('db')


def ml_backend_url(uri: list = ('ml_backend',), **kwargs) -> \
        str:
    """
    拼接ml backend请求链接
    'import': '/api/ml_backend/import',            # 导入
    'export': '/api/ml_backend/export/',           # 导出
    'preprocess': '/api/ml_backend/preprocess',    # 清洗
    'predict': '/api/ml_backend/predict',          # 预标注普通/0样本
    'training': '/api/ml_backend/training',        # 训练
    'cancel': '/api/ml_backend/cancel',            # 训练
    :param opt:
    :param uri:
    :param kwargs:
    :return:
    """

    domain = settings.ML_BACKEND_DOMAIN
    if not domain:
        raise Exception('ML BACKEND DOMAIN NOT CONFIG.')

    return os.path.join(domain, 'api', *uri)


def ml_backend_request(
        uri: list, method: str = 'get', params={}, data={}, json={}
):
    """
    {
    "status": 0,
    "errorInfo": "",
    "data": {
            "download": url
            }
    }
    :param uri:
    :param method:
    :param params:
    :param data:
    :param json:
    :return:
    """
    ml_url = ml_backend_url(uri=uri)
    if 'export' in uri:
        algorithm_url = ''
        if 'url' in params:
            algorithm_url = params.pop('url')
        ml_url = os.path.join(ml_url, algorithm_url)

    logger.info(
        'ML Request url:, ', ml_url, '\nparams:', params, '\ndata:', data
    )
    session = getattr(requests, method)
    response = session(url=ml_url, params=params, data=data, json=json)
    rsp_data = response.json()
    logger.info('ML response: ', rsp_data)
    rsp_state = rsp_data.get('status')
    if rsp_state == 0:
        return True, rsp_data.get('data')
    else:
        return False, rsp_data.get('errorInfo')
