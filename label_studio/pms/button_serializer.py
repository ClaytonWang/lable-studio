"""
  > FileName: serializer.py
  > Author: Yin
  > Mail: jindu.yin@digitalbrain.cn
  > CreatedTime: 2022/04/17 17:05
"""

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField
from .models import PmsPage
from .models import PmsButton


"""
按键权限
"""


class PmsBtnCreatedSerializer(ModelSerializer):
    """
    """
    # page =
    class Meta:
        model = PmsButton
        fields = '__all__'


class PmsBtnUpdatedSerializer(PmsBtnCreatedSerializer):
    code = CharField(required=False)
    page = CharField(required=False)
    pass


class PmsBtnListSerializer(ModelSerializer):

    # created_at = SerializerMethodField()
    # updated_at = SerializerMethodField()
    #
    # @staticmethod
    # def get_created_at(obj):
    #     return format_datetime(obj.created_at)
    #
    # @staticmethod
    # def get_updated_at(obj):
    #     return format_datetime(obj.updated_at)

    class Meta:
        model = PmsButton
        fields = '__all__'


class PmsBtnDetailSerializer(PmsBtnListSerializer):
    pass

