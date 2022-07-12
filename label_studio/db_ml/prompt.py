#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : prompt.py
  > CreateTime : 2022/7/12 21:30
"""
import os
import torch
from transformers import BartForSequenceClassification, BertTokenizer
from projects.models import PromptResult


class Predictor:
    def __init__(self, model_path, device='cpu'):
        self.model = BartForSequenceClassification.from_pretrained(
                    model_path, num_labels=3,  problem_type='single_label_classification').to(device)
        self.model.eval()
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.device = device
        self.id2class = {0: '很差', 1:'较差', 2:'一般'}

    def process(self, text):
        # text = (server, client)
        input_ids = self.tokenizer.encode(text)
        return input_ids

    def predict(self, text):
        input_ids = self.process(text)
        input_ids = torch.tensor([input_ids]).to(self.device)
        logits = self.model(input_ids=input_ids).logits
        logits = torch.softmax(logits, dim=1)
        confidence, indices = logits.max(dim=1)
        return self.id2class[indices.item()], confidence.item()


def job_prompt(**kwargs):
    text = kwargs.get('text')
    task_id = kwargs.get('task_id')
    project_id = kwargs.get('project_id')
    db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(db_ml_dir, 'model_prompt')
    predictor = Predictor(model_path=model_path, device='cpu')
    res_text, confidence = predictor.predict(text)
    print('prompt : ', res_text, 'confidence:', confidence)
    result = {
        "task": text,
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
    c = PromptResult(
        project_id=project_id,
        task_id=task_id,
        metrics=result
    )
    c.save()


if __name__ == '__main__':
    db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(db_ml_dir, 'model_prompt')

    predictor = Predictor(model_path=model_path, device='cpu')
    sens = ['等着做活动[捂脸]',
            '多久好',
            '每个人遇到这类的问题都要自己去反馈吗？',
            '@市公司-业务支撑中心-郭辰 还是不行',
            '现在进去还占着，用户想换个号码，不要这个预占的号码',
            '解除不了，过半个小时再试试吧',
            '13736082694，早上开的花卡，打了个电话，现在欠费了[裂开]客户都要投诉了',
            '大概多久能好呀']
    for sen in sens:
        print(predictor.predict(sen))
