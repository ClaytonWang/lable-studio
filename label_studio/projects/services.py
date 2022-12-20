# -*- coding: utf-8 -*-
"""
    >File    : services.py.py
    >Author  : YJD
    >Mail    : jindu.yin@digitalbrain.cn
    >Time    : 2022/11/22 13:41
"""

from projects.models import PromptTemplates


def get_template(project_id):

    template_list = PromptTemplates.objects.filter(project_id=project_id).values(
        'template', 'label', 'project__template_type'
    )
    if not len(template_list):
        return []

    template_type = template_list[0]['project__template_type']

    if 'conversational-generation' == template_type:
        result = dict()
        for item in template_list:
            label_str = item.get('label', '')
            labels = label_str.split('|||') if label_str else ''
            tmp = item['template']
            for label in labels:
                if label not in result:
                    result[label] = [tmp]
                else:
                    result[label] = result[label] + [tmp]
        return result
    else:
        return [item['template'] for item in template_list]


def conversational_generation_add_template(project_id, label):
    """
    [dlg]请生成[lb]相关回复
    [dlg]你可以咨询[lb]相关问题
    """

    objects = []
    template = ['[dlg]请生成[lb]相关回复', '[dlg]你可以咨询[lb]相关问题']
    for tmp in template:
        obj = PromptTemplates(project_id=project_id, template=tmp, label=label)
        objects.append(obj)

    PromptTemplates.objects.bulk_create(objects)
