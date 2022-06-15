# -*- coding: utf-8 -*-
# @Time : 2022/6/14 17:00
# @Author : qingquan
# @File : rule_clean.py
import os
import json
import tqdm
import string
import numpy as np
import shutil
import sys
import re
from zhon.hanzi import punctuation
import copy
import time
import jieba_fast


class RuleClean:
    r"""A class to filter the original data based on rules.

    Example::
        >>> num_process = 24
        >>> parent_path = '/root/yuanfu/Data/rule_data/ASR'
        >>> save_path = '/root/yuanfu/Data/rule_data/ruled_data'
        >>> df = DataFilter(parent_path, save_path, num_process)
        >>> df.run()
    """
    def __call__(self, _str):
        return self.clean(_str)

    def __init__(self):
        self.special_token = ['[NUM]', '[SPECIAL]']

        self.rep_map = {
            re.compile(r'[0-9]+[a-zA-Z]*'): '[NUM]',
            re.compile(r'[零幺二三四五六七八九十]{2,}(?=[个元号块]|的号|尾号|[\u4e00-\u9fa5]{0,2}号码|[\u4e00-\u9fa5]{0,2}机)'): '[NUM]',
            re.compile(r'(?<=[号])[零幺二三四五六七八九十]{2,}]'): '[NUM]',
            re.compile(r'(?<=代表|客服|号是)[零幺二三四五六七八九十]{2,}]'): '[NUM]',
            re.compile(r'[a-zA-Z]{2,}'): '[E_WORD]',
            re.compile(r'[?？]嗯$'): '',
        }
        self.pat_reverse = re.compile(r'[？?。.、!！，,][呀了吧么吗呢呗哇啦啊哩哈喽呵呐咯哟嘛噢呦]')
        self.pat_digit = re.compile(r'(?<=\D)1\d{10}')
        self.pat_ch_digit = re.compile(
            r"[\u58f9\u8d30\u53c1\u8086\u4f0d\u9646\u67d2\u634c\u7396\u96f6\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u5e7a]{11}")
        self.cut = jieba_fast.lcut

    def _num_match(self, pattern, s):
        """Match a number"""
        match = pattern.search(s, 0)
        if match:
            index = match.span()
            s = s.replace(s[index[0]:index[1]], self.special_token[0])
            return s, True
        return s, False

    def _del_ph_num(self, Q):
        """去除电话号码"""
        #     Q = Q.replace(' ','')
        Q, num_flag = self._num_match(self.pat_digit, Q)
        Q, num_flag = self._num_match(self.pat_ch_digit, Q)
        return Q

    def _del_Punc(self, Q):
        """去除倒数第二个标点符号及后面那个字"""
        if len(Q) < 3:
            return Q
        if Q[-2] in punctuation:
            return Q[:-2]
        return Q

    def _del_Redun(self, Q):
        """去除重复的两个字、三个字、四个字"""
        Refin_Q = list(copy.deepcopy(Q))
        for j in range(len(Q)):
            if j + 14 < len(Q) and Q[j:j + 7] == Q[j + 7:j + 14]:
                Refin_Q[j:j + 7] = ["TMP"] * 7
            elif j + 12 < len(Q) and Q[j:j + 6] == Q[j + 6:j + 12]:
                Refin_Q[j:j + 6] = ["TMP"] * 6
            elif j + 10 < len(Q) and Q[j:j + 5] == Q[j + 5:j + 10]:
                Refin_Q[j:j + 5] = ["TMP"] * 5
            elif j + 8 < len(Q) and Q[j:j + 4] == Q[j + 4:j + 8]:
                Refin_Q[j:j + 4] = ["TMP"] * 4
            elif j + 6 < len(Q) and Q[j:j + 3] == Q[j + 3:j + 6]:
                Refin_Q[j:j + 3] = ["TMP"] * 3
            elif Q[j:j + 2] == Q[j + 2:j + 4]:
                Refin_Q[j:j + 2] = ["TMP"] * 2
        return ''.join(Refin_Q).replace("TMP", "")

    def _A_isNum(self, s):
        """检测回答是否为纯数字"""
        if s.isnumeric():
            return self.special_token[1]
        elif s[:-1].isnumeric():
            return self.special_token[1]
        return s
        # 发现bug 最后一位为标点没有被删除

    def _multi_replace(self, sen, rep_map=None, pat=None):
        """
        Replace string by reg expressions
        :param sen:
        :param rep_map:
                {
                re.compile(r'[0-9]+[a-zA-Z]*'): '[NUM]',
                re.compile(r'[a-zA-Z]{2,}'): '[E_WORD]',
                re.compile(r'[?？]嗯$'): '',
                }
        :param pat:
                re.compile(r'[？?。.、!！，,][呀了吧么吗呢呗哇啦啊哩哈喽呵呐咯哟嘛噢呦]')
        :return:
        """
        be_replaced = []  # 被替换的子串
        to_replace = []  # 替换的子串
        if rep_map:
            for pat, rep in rep_map.items():
                res = re.findall(pat, sen)
                be_replaced.extend(res)
                to_replace.extend([rep_map[pat]] * len(res))
        elif pat:
            res = re.findall(pat, sen)
            be_replaced.extend(res)
            to_replace.extend([token[1] + token[0] for token in res])

        if be_replaced:
            sorted_be_replaced_index = sorted(range(len(be_replaced)), key=lambda x: be_replaced[x], reverse=True)
            new_be_replace = [re.escape(be_replaced[i]) for i in sorted_be_replaced_index]
            new_to_replace = [to_replace[i] for i in sorted_be_replaced_index]
            Capt = lambda x: new_to_replace[new_be_replace.index(re.escape(x.group(0)))]  # Capt:CapterString(捕获字符串)
            replaced_sen = re.sub("|".join(new_be_replace), Capt, sen)
            return replaced_sen
        else:
            return sen

    def _de_dup(self, lst):
        """Remove duplicated items"""

        def inner_de_dup(lst, num):
            to_remove_idxs = []
            this_ele = lst[:num]
            for i in range(len(lst) - num + 1):
                if lst[i + num:i + num * 2] == this_ele:
                    for j in range(i + num, i + num * 2):
                        to_remove_idxs.append(j)
                this_ele = lst[i + 1:i + 1 + num]
            useful_idxs = [i for i in range(len(lst)) if i not in to_remove_idxs]
            useful_eles = np.array(lst)[useful_idxs]
            return useful_eles.tolist()

        for num in range(1, len(lst) // 2, 1):
            lst = inner_de_dup(lst, num)
        return ''.join(lst)

    def clean(self, _str):
        elapse_time = {
            '替换空格': 0,
            '调整“符号语气词”顺序': 0,
            '正则替换': 0,
            'jieba切词': 0,
            '去除重复子串': 0,
        }  # The elapsed time of each rule

        # 去除电话号码
        # _str = self._del_ph_num(_str)
        # 去除倒数第二个标点符号及后面那个字
        # _str = self._del_Punc(_str)
        # 去除重复的两个字、三个字、四个字
        # _str = self._del_Redun(_str)
        # 检测回答是否为纯数字
        # _str = self.__str_isNum(_str)

        # 替换空格
        elapse_time['替换空格'] -= time.time()
        _str = _str.replace(' ', '').strip()
        elapse_time['替换空格'] += time.time()
        # 形如"。啊"的替换为"啊。"
        elapse_time['调整“符号语气词”顺序'] -= time.time()
        _str = self._multi_replace(_str, pat=self.pat_reverse)
        elapse_time['调整“符号语气词”顺序'] += time.time()
        # 替换map
        elapse_time['正则替换'] -= time.time()
        _str = self._multi_replace(_str, rep_map=self.rep_map)
        elapse_time['正则替换'] += time.time()
        # jieba切词
        elapse_time['jieba切词'] -= time.time()
        _str = self.cut(_str)
        elapse_time['jieba切词'] += time.time()
        # 去除重复子串
        elapse_time['去除重复子串'] -= time.time()
        _str = self._de_dup(_str)
        elapse_time['去除重复子串'] += time.time()

        print("Elapsed time n seconds: ", elapse_time)
        return _str


if __name__ == '__main__':

    _str = '那我我这边昨天我这边打10086的电话，这边人工服务，这这不是司机。啊'
    res = RuleClean()(_str)
    print(res)
