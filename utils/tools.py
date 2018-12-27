from pytz import timezone
from django.conf import settings
from config import PASSWORD_SALT
import hashlib
import json


def datetime_convert(datetime):
    """
    转换 datetime object 为人性化显示时间
    :param datetime: datetime object
    :return: str
    """
    if not datetime:
        return None
    tz = timezone(settings.TIME_ZONE)
    dateval = datetime.astimezone(tz)
    return dateval.strftime('%Y-%m-%d %H:%M:%S')


def password_hash(password):
    """
    对密码进行加盐哈希
    :param password: str or int, 密码
    :return: str, 哈希结果
    """
    h = hashlib.sha256()
    p = str(password) + PASSWORD_SALT
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
    except:
        d = {}
    return d

