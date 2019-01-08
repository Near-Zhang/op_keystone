from django.core.exceptions import ObjectDoesNotExist
from utils.tools import import_string


def get_object_from_model(model, **kwargs):
    """
    从模型中获取单个对象
    :param model: str|model object, 模型
    :param kwargs: 过滤参数
    :return:
    """
    if isinstance(model ,str):
        model = import_string(model)
    try:
        obj = model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        obj = None
    return obj

