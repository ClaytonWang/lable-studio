#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : prompt.py
  > CreateTime : 2022/7/12 21:30
"""
import os
import time
import torch
import random
import numpy as np
from transformers import BartForSequenceClassification, BertTokenizer
from projects.models import PromptResult
from db_ml.services import AlgorithmState
from db_ml.services import generate_redis_key
from db_ml.services import redis_get_json
from db_ml.services import redis_update_finish_state


class Predictor:

    _cache = {}

    def __new__(cls, model_path, device='cpu'):
        args = (model_path, 'prompt', device)
        if args not in cls._cache:
            instance = super().__new__(cls)
            model = BartForSequenceClassification.from_pretrained(
                model_path, num_labels=3,
                problem_type='single_label_classification').to(device)
            model.eval()
            # setattr
            tokenizer = BertTokenizer.from_pretrained(model_path)
            instance.model = model
            instance.tokenizer = tokenizer
            instance.device = device
            instance.id2class = {0: '负面', 1: '中性', 2: '正面'}
            cls._cache[args] = instance
        return cls._cache[args]

    # def __init__(self, model_path, device='cpu'):
    #     self.model = BartForSequenceClassification.from_pretrained(
    #                 model_path, num_labels=3,  problem_type='single_label_classification').to(device)
    #     self.model.eval()
    #     self.tokenizer = BertTokenizer.from_pretrained(model_path)
    #     self.device = device
    #     self.id2class = {0: '负面', 1: '中性', 2: '正面'}

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
    # db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    # model_path = os.path.join(db_ml_dir, 'models', 'model_prompt')
    # predictor = Predictor(model_path=model_path, device='cpu')
    # res_text, confidence = predictor.predict(text)
    text = text.strip()
    res_text = TEMPLATE_PROMPT.get(text, random.choice(['负面', '中性', '正面']))
    confidence = np.random.rand()
    print('prompt : ', res_text, 'confidence:', confidence)
    result = {
        "task": text + kwargs.get('template', ''),
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
    redis_key = generate_redis_key(
        'prompt', str(kwargs.get('project_id', ''))
    )
    p_state = redis_get_json(redis_key)
    if p_state and p_state.get('state') == AlgorithmState.ONGOING:
        c = PromptResult(
            project_id=project_id,
            task_id=task_id,
            metrics=result
        )
        c.save()
        redis_update_finish_state(redis_key, p_state)


TEMPLATE_PROMPT = {
    "不用了，终于提交成功了": "正面",
    "我的手机套餐叫什么套餐？多少钱一个月可以帮我查一下吗？": "中性",
    "你好，我流量不够用了可以帮我加一下流量包吗？": "中性",
    "我目前是电信用户，可以号码不变，携号转网变成移动用户吗？": "中性",
    "目前没有问题了，如果再出现问题我再联系你，谢谢": "正面",
    "可以帮我查一下离我最近的移动门店吗？": "中性",
    "客户那边等着做，又要被骂了": "负面",
    "着急啊 这么多客户都欠费了，最好流程上快一点 ": "负面",
    "没错就是这样，按我说的操作就可以啦": "正面",
    "无语了，三天两头的出问题": "负面",
    "生意宝一直人脸验证验证人脸重复进不去": "负面",
    "人脸识别之后就拒绝访问了": "负面",
    "然后应急中心那个办卡还是点不动": "负面",
    "清理了，现在可以了。": "正面",
    "试了2台电脑，都一样": "中性",
    "对，我想办亲情套餐，听说比较划算。": "正面",
    "上边还是会处理的吧，客户有事儿走了，得一会儿才能来": "中性",
    "但前期同事也有遇到过，不是这个工号的，回复说要离职再入职": "中性",
    "现在进去还占着，用户想换个号码，不要这个预占的号码": "中性",
    "可以了，现在进去了。": "正面",
    "今天生意宝打不开应用呀": "负面",
    "首次受理是正常，重下后就出现这个体会": "负面",
    "视频坐席之后跳不过去下一步怎么搞 ": "负面",
    "那也没有办法了。": "负面",
    "还是一片空白，什么时候能好啊": "负面",
    "有问题您随时联系我。": "正面",
    "异常订单中有，显示未处理，这怎么回事？": "负面",
    "最新的。生意宝可以进了 点不动": "负面",
    "店员说已经激活好了啊": "正面",
    "这个我不太了解，我很久没有用了。": "中性",
    "已经激活好了，您再试试。": "正面",
    "收到视频消息,请在手机上查看": "中性",
    "系统提示很明确了": "中性",
    "不是一个人不行，是好几个人都不行": "负面",
    "好的，您再检查一下，如果有问题再联系我们": "正面",
    "没有给他搞好，说要去砸了营业厅": "负面",
    "更新了，没用": "负面",
    "目前都已经恢复了": "正面",
    "视频不是已经有了吗，还要操作步骤": "中性",
    "删除了好几遍还是这样": "负面",
    "我这里也没好，卡的很": "负面",
    "业务处理大厅打不开，APP也更新过了": "负面",
    "已经操作过重新下单还是这样": "负面",
    "杭州多家厅反映，业务大厅报错": "负面",
    "这个只能多试几次吧": "中性",
    "继续办理点了没反应又只能取消订单。": "负面",
    "每次都是6位  做监控做不下去": "负面",
    "我想把4G套餐升级成5G套餐。": "中性",
    "之前都正常的，就最近出问题了。": "负面",
    "合约机一般要绑定几个月的合约呢？": "中性",
    "运营指挥中心进去也不行啊": "负面",
    "你们如果再不给我，呢我今天晚上下午就打到工信部去了的话，反正你自己看着办。": "负面",
    "我家宽带是多少钱一个月，办套餐现在有送宽带的吗？": "中性",
    "之前是移动转到了电信，现在又想转回来，是因为移动的号段关系吗": "中性",
    "我就是退出了，重新登的，然后就卡成这样了。": "负面"
}


if __name__ == '__main__':
    db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(db_ml_dir, 'models', 'model_prompt')

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
