from pytz import timezone
from django.conf import settings


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