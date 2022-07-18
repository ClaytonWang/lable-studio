#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : bart_for_turn.py
  > CreateTime : 2022/6/14 14:23
"""
import os
import torch
import time
import json
import yaml
import logging
from torch.nn.utils.rnn import pack_sequence, pad_packed_sequence, pad_sequence
from transformers import BertTokenizer, BartForConditionalGeneration, \
    Text2TextGenerationPipeline


class Inference:

    def __init__(self, model_path):
        self.model_path = model_path
        yaml_dir = os.path.join(self.model_path, 'special_tokens.yaml')
        special_tokens = open(yaml_dir)
        self.special_tokens = yaml.load(special_tokens, Loader=yaml.FullLoader)[
            'special_tokens']
        self.tokenizer = BertTokenizer.from_pretrained(
            self.model_path, additional_special_tokens=self.special_tokens
        )
        self.model = BartForConditionalGeneration.from_pretrained(
            self.model_path)  # .to('cuda:1')  # 可以使用gpu
        self.model.eval()

    def __call__(self, dialog: list) -> list:
        return self.generate(dialog)

    def process(self, dialog):
        # dialog格式: [{'段落-1':xxxx}, {'段落-2':xxx},...]
        dia_ids = []
        dia_tokens = []
        turn_ids = []
        for k_v in dialog:
            for speaker, sen in k_v.items():
                sen_ids = self.tokenizer.encode(sen, add_special_tokens=False)
                sen_token = self.tokenizer.convert_ids_to_tokens(sen_ids)
                if speaker == '段落-1':
                    tar_ids = [6] * len(sen_ids)
                else:
                    tar_ids = [7] * len(sen_ids)
                dia_ids.extend(sen_ids)
                turn_ids.extend(tar_ids)
                dia_tokens.extend(sen_token)
        dia_ids = [101, 3] + dia_ids + [102]
        turn_ids = [101] + turn_ids
        # return dia_ids, turn_ids
        return dia_tokens, torch.tensor(dia_ids), torch.tensor(turn_ids)

    def paired_collate_fn(self, insts):
        enc_input = [src for tokens, src, tgt in insts]
        dec_input = [tgt[:-1] for tokens, src, tgt in insts]
        all_tokens = [tokens for tokens, src, tgt in insts]
        labels = [tgt[1:] for tokens, src, tgt in insts]
        # encoder 打padding
        enc_input_packed = pack_sequence(enc_input, enforce_sorted=False)
        enc_input_padded, word_lens = pad_packed_sequence(enc_input_packed,
                                                          batch_first=True)  # 序列打padding
        enc_mask = enc_input_padded.gt(0)
        # decoder padding
        dec_input_packed = pack_sequence(dec_input, enforce_sorted=False)
        dec_input_padded, word_lens = pad_packed_sequence(dec_input_packed,
                                                          batch_first=True)
        dec_mask = dec_input_padded.gt(0)
        return enc_input_padded, enc_mask, dec_input_padded, dec_mask, labels, all_tokens

    def generate(self, dialog):
        # dialog格式: [{'段落-1':xxxx}, {'段落-2':xxx},...]
        inputs = self.paired_collate_fn([self.process(dialog)])
        enc_input_padded, enc_mask, dec_input_padded, dec_mask, labels, all_tokens = inputs
        all_tokens = all_tokens[0]
        logits = self.model(enc_input_padded, enc_mask, dec_input_padded,
                            dec_mask).logits[0]
        _, indices = logits.max(dim=1)

        sens = []
        last_spk = None
        for j, spk in enumerate(indices):
            spk = spk.item()
            if last_spk != spk:
                if j > 0:
                    sens.append({last_spk: sen})
                sen = ''
            sen += all_tokens[j]
            if j < len(indices) - 1:
                last_spk = spk
            else:
                sens.append({last_spk: sen})
        return sens


def bart_for_turn(dialog):
    db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(db_ml_dir, 'models', 'model_bart_for_turn_path')
    return Inference(model_path=model_path)(dialog)


if __name__ == '__main__':
    t_dialog = [
        {
            '段落-1': '您好，中国移动客服代表316号，请问您是137号码的机主吗？没有没有。嗯对对对。啊就是呃林女士你好，就是我们这里有个话费减免活动，啊免费帮您减话费的，然后两年来两就有有两年的活动期活动下来帮你剪了那个340块钱话费，然后的话只需要您预存10块钱预存的10块钱当天就返还到您手机账户上了，就是扣除您10块钱嘛就当天就返还到您手机账户上，还有就是你每个月保底消费达到38就可以了，那您看我这里帮您办理了好。嗯行。吧嗯好，反正就每每个月免费帮您减话费的，比您现在话费要少，啊那为了您的使用安全，请问您手机号是13757484950。唉等一下那我之前有个什么保底的那个冲突吗？啊不冲突，你只要每个月我看你每个月话费都60多块钱已经达到了的。没有冲突的您。不是，我之前好像也有一个什么39还是59。吧噢这个这个没关系的，你因为我们这个话费啊这个消就是您达到了这个消费水平就可以了，是这样的，跟您之前跟您换任何套餐是没有关系的好吧？你想要干更改其他套餐都没关系，都不影响这个话费减免，因为我看您之前您现在有一个话费抵扣了，每个月减4块钱。呢是这样的，啊好，因为您账单上面看不出来的，我们这里可以看出来的，不然的话您实际费用就比您现在高4块钱，那之后，我们办理这个活动就比您之前力度大了，嘛我跟您说一下。啊我怎么不知道？嗯嗯生是当月生效的，那活动期24个月，每个月保底消费38元，不包括代收及预缴费用，国际费用、外部权益费用、消费抵扣权是每个月自动激活的，跟您说一下每个月是怎么减话费的，啊那一1~4个月，每个月减36块钱，5~6个月每个月减26块钱，7~24个月，每个月减8块钱，啊那请您两年内保持在网络活动期间内，您终止活动或退出新情况则停止，月消费减免必须支付未履行合约期保底消费总金额的30%。那剩余未使用未生效的消费理由会回收，那办理时我们会先从您账户中扣除10块钱来参加活动，活动生效就立即反冲的，请确保10月29日前全车手机本金余额大于10元以上，且手机状态正常。办理成功我们会下发短信的，那您是一个亲情网用户，嘛使用亲情网短号拨打网内语音也是更方便的，那后续如果其他优惠活动再通过电话或短信等方式联系，你好吧？唉好，李女士，现在最后一步啊为您转接语音台，就你按一号键确认办理就可以了，好吧？唉好，转接中请按1。唉女士女士这一成功过来，那稍后你会收到一条针对我个人服务的评分短信，就麻烦您有空的时候给个10分好评可以吗？唉好，我自己就不打扰您了，祝您生活愉快，啊再见。啊嗯对。再见。'
        }
    ]
    result = Inference()(t_dialog)
    for item in result:
        print(item)
