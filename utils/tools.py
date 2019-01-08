from pytz import timezone
from datetime import datetime, timedelta
from django.conf import settings
from importlib import import_module
import hashlib
import json
import uuid


def get_datetime_with_tz(datetime_obj=None, **kwargs):
    """
    获取当前 datetime 对象，或者转化指定 datetime 对象到指定时区，也可以进行时间增减
    :param datetime_obj: datetime object
    :param kwargs: timedelta 参数
    :return: datetime object
    """
    if not datetime_obj:
        datetime_obj = datetime.now()

    tz = timezone(settings.TIME_ZONE)
    datetime_with_tz = datetime_obj.astimezone(tz)

    if kwargs:
        return datetime_with_tz + timedelta(**kwargs)
    return datetime_with_tz


def datetime_convert(datetime_obj=None):
    """
    转换 datetime object 为指定时区的人性化显示时间
    :param datetime_obj: datetime object
    :return: str
    """
    datetime_with_tz = get_datetime_with_tz(datetime_obj)
    return datetime_with_tz.strftime('%Y-%m-%d %H:%M:%S')


def password_hash(password):
    """
    对密码进行加盐哈希
    :param password: str or int, 密码
    :return: str, 哈希结果
    """
    h = hashlib.sha256()
    p = str(password) + settings.PASSWORD_SALT
    h.update(bytes(p, encoding='utf8'))
    return h.hexdigest()


def json_loader(json_str):
    """
    反序列化 json 字符串并返回结果, 若不是标准 json 返回错误 JsonResponse 对象
    :param json_str: json 字符串
    :return: dict
    """
    if not json_str:
        return {}
    try:
        d = json.loads(json_str)
    except ValueError:
        d = {}
    return d


def generate_mapping_uuid(namespace_hex, mapping_str):
    """
    获取指定命名空间和字符串映射的 uuid
    :param namespace_hex: str, 命名空间十六进制 uuid
    :param mapping_str: str, 映射的字符串
    :return: str, 十六进制 uuid
    """
    namespace = uuid.UUID(hex=namespace_hex)
    uuid_hex = uuid.uuid3(namespace, mapping_str).hex
    return uuid_hex


def generate_unique_uuid():
    """
    获取唯一性的 uuid
    :return: str, 十六进制 uuid
    """
    uuid_hex = uuid.uuid1().hex
    return uuid_hex


def import_string(dotted_path):
    """
    动态加载以字符串表示的模块中的属性或类
    :param dotted_path: str, [包.]模块.[类|属性]
    :return: class|method
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        return None

    m = import_module(module_path)

    try:
        return getattr(m, class_name)
    except AttributeError:
        return None

