from pytz import timezone
from datetime import datetime, timedelta
from django.conf import settings
from op_keystone.exceptions import *
from importlib import import_module
import hashlib
import json
import uuid
import time
import geoip2.database
import string
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import requests
from requests.exceptions import RequestException


def get_datetime_with_tz(datetime_obj=None, datetime_tuple=None, **kwargs):
    """
    获取当前 datetime 对象，或者转化指定 datetime 对象到指定时区，也可以进行时间增减
    :param datetime_obj: datetime object
    :param kwargs: timedelta 参数
    :return: datetime object
    """
    if not datetime_obj:
        if datetime_tuple:
            datetime_obj = datetime(*datetime_tuple)
        else:
            datetime_obj = datetime.now()

    tz = timezone(settings.TIME_ZONE)
    datetime_with_tz = datetime_obj.astimezone(tz)

    if kwargs:
        return datetime_with_tz + timedelta(**kwargs)
    return datetime_with_tz


def datetime_to_humanized(datetime_obj=None):
    """
    转换 datetime 对象为指定时区的人性化显示
    :param datetime_obj: datetime object
    :return: str
    """
    datetime_with_tz = get_datetime_with_tz(datetime_obj)
    return datetime_with_tz.strftime('%Y-%m-%d %H:%M:%S')


def datetime_to_timestamp(datetime_obj=None):
    """
    转换 datetime object 为时间戳
    :param datetime_obj: datetime object
    :return: int, 时间戳
    """
    if not datetime_obj:
        return time.time()

    timetuple = datetime_obj.timetuple()
    return time.mktime(timetuple)


def timestamp_to_datetime(timestamp=None):
    """
    转换时间戳为 datetime object
    :param timestamp: int, 时间戳
    :return: datetime object
    """
    if timestamp is None or type(timestamp) != int:
        timestamp = time.time()

    datetime_obj = datetime.fromtimestamp(timestamp)
    return get_datetime_with_tz(datetime_obj)


def password_to_hash(password):
    """
    对密码进行加盐哈希
    :param password: str or int, 密码
    :return: str, 哈希结果
    """
    h = hashlib.sha256()
    p = str(password) + settings.PASSWORD_SALT
    h.update(bytes(p, encoding='utf8'))
    return h.hexdigest()


def json_dumper(obj):
    """
    序列化对象为 json 字符串并返回结果
    :param obj: obj
    :return: json str
    """
    if obj is None:
        return ''
    try:
        return json.dumps(obj)
    except ValueError:
        return ''


def json_loader(json_str):
    """
    反序列化 json 字符串并返回结果
    :param json_str: str|byte, json 形式
    :return: dict
    """
    if json_str is None or json_str == "":
        return {}
    try:
        return json.loads(json_str)
    except ValueError:
        return {}


def generate_mapping_uuid(namespace_hex, mapping_str):
    """
    获取命名空间和字符串映射的 uuid
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


def paging_list(total_list, page=1, page_size=None):
    """
     对于总数据列表进行分页，并返回当前页的数据列表
    :param total_list: list, 数据总列表
    :param page: int, 页数
    :param page_size: int, 页大小
    :return: dict, 包含数据总数、当前页数据列表的字典
    """
    total_count = len(total_list)
    if not page_size:
        page_size = total_count
    start_index = (int(page) - 1) * int(page_size)
    end_index = start_index + int(page_size)
    current_page_list = total_list[start_index:end_index]

    return {
        'total': total_count,
        'data': current_page_list
    }


def judge_private_ip(ip):
    """
    判断 IP 是否为内网 IP
    :param ip: str, IP 地址
    :return: bool
    """
    sections = ip.split('.')
    sections = [ int(s) for s in sections ]
    private = False

    if sections[0] == 10:
        private = True
    elif sections[0] == 172 and 16 <= sections[1] < 32:
        private = True
    elif sections[0] == 192 and sections[1] == 168:
        private = True
    return private


def request_external_api(method, url, data=None, json_body=False):
    """
    请求外部接口
    :param method: str, 请求方法
    :param url: str, 请求 url
    :param data: dict, 请求数据
    :param json_body: body 是否以 json 而非表单形式发送
    :return: request response object
    """
    try:
        request_func = getattr(requests, method)
        if method == 'get':
            response = request_func(url, params=data).json()
        else:
            if json_body:
                response = request_func(url, json=data).json()
            else:
                response = request_func(url, data=data).json()

        return response

    except RequestException:
        raise RequestBackendError(method, url)


def ip_to_location(ip):
    """
    解析 IP 为其对应的物理位置
    :param ip: str, IP 地址
    :return: str
    """
    reader = geoip2.database.Reader('utils/extra_files/GeoLite2-City.mmdb')
    response = reader.city(ip)

    location_list = []
    for k in ['continent', 'country', 'subdivisions', 'city']:
        try:
            attr = getattr(response, k)
            try:
                name_dict = attr.names
            except AttributeError:
                name_dict = attr[0].names
            v = name_dict.get('zh-CN', '')
            location_list.append(v)
        except (AttributeError, IndexError):
            continue

    return ' '.join(location_list)


def generate_captcha_img(size=(120, 40), length=4, draw_lines=True,
                         lines_range=(2, 3), draw_points=True, point_chance=3):
    """
    :param size: tuple(width, height), 图片尺寸
    :param length: 验证码字符个数
    :param draw_lines: 是否划干扰线
    :param lines_range: 干扰线的条数范围，格式元组，默认为(1, 2)
    :param draw_points: 是否画干扰点
    :param point_chance: 干扰点出现的概率，大小范围[0, 100]
    :return: [0]: PIL Image object
    :return: [1]: 验证码图片中的字符串
    """
    # 设置验证码颜色和字体
    mode = "RGB"
    bg_color = (255, 255, 255)
    fg_color_list = [
        (0, 0, 255),
        (255, 0, 0),
        (255, 0, 255),
        (0, 100, 0),
        (238, 118, 0)
    ]
    font_size = 22
    font_type_file = "utils/extra_files/Monaco.ttf"

    # 随机字符集，除去可能干扰的字母(i、I、l、L、o、O、z、Z)和数字(0、1、2)
    letter_lowercase = re.sub('[iloz]', '', string.ascii_lowercase)
    letter_uppercase = letter_lowercase.upper()
    digits_number = string.digits[3:]
    chars = ''.join((letter_lowercase, letter_uppercase, digits_number))

    # 创建图形和画笔
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)

    # 获取随机字符串
    random_char_list = random.sample(chars, length)
    captcha_str = ''.join(random_char_list)

    # 绘制字符
    font = ImageFont.truetype(font_type_file, font_size)
    width, height = size
    for c in random_char_list:
        font_width, font_height = font.getsize(c)
        fg_color = fg_color_list[random.randint(0, len(fg_color_list) - 1)]
        begin_width = (width / length - font_width) / 2 + random_char_list.index(c) * width / (length + 1)
        begin_height = (height - font_height) / 3
        draw.text((begin_width, begin_height), c, font=font, fill=fg_color)

    # 绘制干扰线
    if draw_lines:
        line_num = random.randint(*lines_range)
        for i in range(line_num):
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    # 绘制干扰点
    if draw_points:
        chance = min(100, int(point_chance))
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    # 图形扭曲参数
    params = [
        1 - float(random.randint(1, 2)) / 100, 0, 0,
        0, 1 - float(random.randint(1, 10)) / 100, float(random.randint(1, 2)) / 500,
        0.001, float(random.randint(1, 2)) / 500
    ]
    img = img.transform(size, Image.PERSPECTIVE, params)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    return img, captcha_str


def send_phone_captcha(phone, expire=60):
    """
    使用腾讯短信接口，发送手机验证码
    :param phone: str, 手机号码
    :param expire: int, 过期秒数
    :return: str, 验证码
    """
    # 定义短信接口参数
    digits_number = string.digits
    sdk_app_id = settings.TX_SMS_APP_ID
    app_key = settings.TX_SMS_APP_KEY
    random_str = ''.join(random.sample(digits_number, 4))
    now_stamp = time.time().__trunc__()
    captcha_str = ''.join(random.sample(digits_number, 6))

    # 请求的相关信息定义
    method = 'post'
    url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms?sdkappid=%s&random=%s' \
          % (sdk_app_id, random_str)
    data = {
        'params': [
            captcha_str,
            expire
        ],
        'sign': "广州君海",
        'tel': {
            'mobile': phone,
            'nationcode': '86'
        },
        'time': now_stamp,
        'tpl_id': 294623
    }
    h = hashlib.sha256()
    abstract = 'appkey=%s&random=%s&time=%s&mobile=%s' % (app_key, random_str, now_stamp, phone)
    h.update(bytes(abstract, encoding='utf8'))
    data['sig'] = h.hexdigest()

    # 请求短信接口并检查发送结果，返回验证码
    response = request_external_api(method, url, data, json_body=True)
    if response.get('result') != 0:
        raise ResponseBackendError(method, url, response.get('errmsg'))
    return captcha_str


def send_email_captcha(email, expire=60):

    pass
