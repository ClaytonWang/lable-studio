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

    if 'intent-classification' == template_type:
        result = dict()
        for item in template_list:
            label = item.get('label')
            if label not in result:
                result[label] = [item['template']]
            else:
                result[label] = result[label] + [item['template']]
        return result
    else:
        return [item['template'] for item in template_list]


