#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : intelligent.py
  > CreateTime : 2022/6/13 17:01
"""
import os
import time
import torch
from transformers import BertTokenizer, BartForConditionalGeneration, Text2TextGenerationPipeline
# from trainer import eval_data


class IntelligentModel:

    def __init__(self, model_path):
        tokenizer = BertTokenizer.from_pretrained(
            model_path,
            additional_special_tokens=['[NUM]', '[E_WORD]']
        )
        # .to('cuda:0')
        fine_tuned_model = BartForConditionalGeneration.from_pretrained(
            model_path
        )
        fine_tuned_model.eval()
        self.fine_tuned_text2text_generator = Text2TextGenerationPipeline(
            fine_tuned_model, tokenizer
        )  # , device=0)  # device=0表示用第0块gpu，不设置device表示用cpu

    def __call__(self, text: list) -> list:
        result = self.fine_tuned_text2text_generator(
            text, max_length=500, num_beams=4
        )
        return [
            dict(generated_text=item['generated_text'].replace(' ', ''))
            for item in result
        ]


def intelligent(text):
    db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(db_ml_dir, 'model_intelligent_path')
    return IntelligentModel(model_path=model_path)(text)


if __name__ == '__main__':
    _db_ml_dir = os.path.dirname(os.path.abspath(__file__))
    _intell_model_path = os.path.join(_db_ml_dir, 'model_intelligent_path')

    _src = ['你这个不不是9点下班了吗？', '嗯昨天可能是月底，她那边应该可能电话量比较多，吧所以说你可能没有及时接通。']
    print(IntelligentModel(model_path=_intell_model_path)(_src))
