# -*- coding: utf-8 -*-
# @Time : 2022/5/9 20:28
# @Author : qingquan
# @File : predict.py
# @Software: PyCharm

import os
import torch
import pandas as pd
from core.redis import redis_get
from transformers import BartForSequenceClassification, BertTokenizer
from tasks.models import Prediction, Task
from db_ml.services import generate_redis_key
from db_ml.services import AlgorithmState

# import torch.nn as nn
# from tasks.models import PredictionDraft
# from db_ml.services import PREDICTION_BACKUP_FIELDS
# from django.db import transaction


class Predictor:
    def __init__(self, model_path,
                 label_file='data/营业厅数字人项目事项v1.0-人工匹配规则枚举.xlsx', device='cpu'):
        self.model = BartForSequenceClassification.from_pretrained(
            model_path, num_labels=9,
            problem_type='single_label_classification').to(device)
        self.model.eval()
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.device = device
        keyword2content = pd.read_excel(label_file, sheet_name='回答类别及内容-纠正')
        keyword = keyword2content[keyword2content.columns[0]].tolist()
        self.id2class = {k: v for k, v in enumerate(keyword)}

    def process(self, text):
        # text = (server, client)
        text = '[SEP]'.join(text).strip()
        input_ids = self.tokenizer.encode(text)
        return input_ids

    def predict(self, text):
        input_ids = self.process(text)
        input_ids = torch.tensor([input_ids]).to(self.device)
        logits = self.model(input_ids=input_ids).logits
        logits = torch.softmax(logits, dim=1)
        confidence, indices = logits.max(dim=1)
        return self.id2class[indices.item()], confidence.item()


def job_predict(*args, **kwargs):
    db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(db_ml_dir, 'model_path')
    label_file = 'data/营业厅数字人项目事项v1.0-人工匹配规则枚举.xlsx'
    label_file_path = os.path.join(db_ml_dir, label_file)
    predictor = Predictor(
        model_path, label_file=label_file_path, device='cpu'
    )
    text = kwargs.get('text')
    task_id = kwargs.get('task_id')
    task = Task.objects.filter(id=task_id).first()

    res_text, confidence = '', 0
    if not task:
        print(f'Task id invalid. Input data: task id [{task_id}]')
        return
    elif task and text:
        res_text, confidence = predictor.predict(text)
    else:
        pass
    # label-studio数据结构
    pre_result = {
        'from_name': 'intent',
        'to_name': 'dialogue',
        'type': 'choices',
        'value': {
            'choices': [res_text], 'start': 0, 'end': 1
        },
    }
    tag_data = dict(
        # project_id=kwargs.get('project_id'),
        task=task,
        result=[pre_result],
        score=round(confidence, 4),

    )
    print(f"results: ....{str(tag_data)}")
    redis_key = generate_redis_key(
        'pre_tags', str(kwargs.get('project_id', ''))
    )
    project_state = redis_get(redis_key)
    if not project_state or \
            bytes.decode(project_state) != AlgorithmState.CANCELED:

        obj, is_created = Prediction.objects.update_or_create(
            defaults=tag_data, task=task
        )
        print('obj:', obj.id, ' auto: ', res_text, ' is_ created:', is_created)
    else:
        print('kwargs:', kwargs, ' cancel')


if __name__ == '__main__':

    _predictor = Predictor('db/model_path', device='cpu')
    sens = [('好的，请问您还有其他业务需要办理吗？您可以跟我说查套餐.查语音.查流量等\u3000[SEP]我不要', '否定'),
            ('好的，正在为您办理XXX业务，业务套餐为XXX元xxx分钟包含XX兆流量，请稍候[SEP]没听见', '默认'),
            ('您的XXX业务办理成功，请问您还有其他业务需要办理查询吗？\u3000[SEP]嗯', '肯定'),
            ('XX先生/女生，您好，欢迎光临中国移动，是否帮您查询名下移动号卡业务，[SEP]没什么问题了', '肯定'),
            (
                '您的语音套餐为XXX分钟、已使用XXX分钟、剩余XXX分钟；为了让您有更好的使用体验，推荐您使用XXX语音加油包，加油包包含xxx元xxx分钟，您需要办理吗？[SEP]暂时没打算',
                '不办理'),
            ('已为您查询到您名下宽带套餐xxx，宽带电视数量XXX即将到期，[SEP]首页', '返回主屏幕'),
            ('业务查询办理成功，请问您还有其他业务需要办理么?[SEP]好的谢谢', '肯定'),
            ('好的，正在为您办理XXX宽带套餐业务，请稍等。[SEP]你刚刚说什么了', '默认'),
            ('业务查询办理成功，请问您还有其他业务需要办理么?[SEP]再说一下', '默认'),
            ('为您推荐最优惠的宽带套餐，以及丰富的智能家居产品，是否需要向您介绍下我们的优惠套餐以及智能家居产品呢？[SEP]不打算做',
             '否定')]
    for sen in sens:
        _text = sen[0].split('[SEP]')
        print(_predictor.predict(_text))
