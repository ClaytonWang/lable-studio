#! /usr/bin/env python3
import numpy as np


# def patch_prompt(templates, dailogue):
#     """
#         patch algorithm
#     """
#     result = {
#                 "task": "我是对话",
#                 "annotation": "正面",
#                 "average": {"正面标签": np.random.rand(), "负面标签": np.random.rand()},
#                 "output":
#                         [{"template": "你好，我是模版A1",
#                          "label": "正面",
#                           "score": "烂片%f" % np.random.rand(),
#                           "wgtedAvg": np.random.rand()},
#                          {"template": "你好，我是模版B",
#                           "label": "负面",
#                           "score": "精品%f" % np.random.rand(),
#                           "wgtedAvg": np.random.rand()}
#                     ]
#             }
#     return result

from db_ml.predict import Predictor


def patch_prompt(templates, dailogue):
    """
        patch algorithm
    """
    _predictor = Predictor('db/model_path', device='cpu')
    res_text, confidence = _predictor.predict(dailogue)

    result = {
                "task": "我是对话",
                "annotation": "正面",
                "confidence": confidence,
                "average": {"正面标签": np.random.rand(), "负面标签": np.random.rand()},
                "output":
                        [{"template": "你好，我是模版A1",
                         "label": "正面",
                          "score": "烂片%f" % np.random.rand(),
                          "wgtedAvg": np.random.rand()},
                         {"template": "你好，我是模版B",
                          "label": "负面",
                          "score": "精品%f" % np.random.rand(),
                          "wgtedAvg": np.random.rand()}
                    ]
            }
    return result
