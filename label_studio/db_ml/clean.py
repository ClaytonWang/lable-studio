#!/usr/bin/env python
# encoding: utf-8

"""
  > Author     : YIN
  > Mail       : jindu.yin@digitalbrain.cn
  > FileName   : clean.py
  > CreateTime : 2022/6/15 14:03
"""
import logging
from tasks.models import TaskDbAlgorithm
from db_ml.clean_rule import RuleClean
from db_ml.clean_intelligent import intelligent
from db_ml.clean_bart_for_turn import bart_for_turn
logger = logging.getLogger('console')


def job_clean(*args, **kwargs):
    """
    调用顺序【轮次纠正】-> 【规则纠正（清洗）】-> 【智能纠正】
    参数kwargs
        project_id
        task_id
        dialog
    :param args:
    :param kwargs:
    :return:
    """
    project_id = kwargs.get('project_id')
    task_id = kwargs.get('task_id')
    dialog = kwargs.get('dialog')
    if not project_id or not task_id:
        logger.warning('Project, task is invalid.')

    algorithm_id = kwargs.get('algorithm_id')
    try:
        # 原数据拼接成 轮次纠正的格式
        dialog_text = ''.join([
            item.get('author', '') + item.get('text', '') for item in dialog
        ])
        turn = bart_for_turn([{'段落-1': dialog_text}])
        intell_text = []
        # 规则
        for index, item in enumerate(turn):
            for k, v in item.items():
                rule_text = RuleClean()(v)
                intell_text.append(rule_text)
                turn[index][k] = rule_text
                break
        # 智能
        intell = intelligent(intell_text)
        for index, item in enumerate(turn):
            for k, v in item.items():
                if index <= len(intell) - 1:
                    turn[index][k] = intell[index].get('generated_text', '')
                break

        # 拼接回对话模式
        result = []
        for item in turn:
            for k, v in item.items():
                result.append(dict(author=str(k), text=v))
                break

        # 数据写回数据库
        TaskDbAlgorithm.objects.filter(id=algorithm_id).update(
            algorithm=result, state=2, remark=''
        )
    except Exception as e:
        TaskDbAlgorithm.objects.filter(id=algorithm_id).update(
            state=3, remark=str(e)
        )


