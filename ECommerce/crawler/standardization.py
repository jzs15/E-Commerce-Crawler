from app.models import *
from mongoengine import *
from ECommerce.settings import DATABASE_NAME
import re

cellphone_brand_list = {
    '华为': ['华为', 'HUAWEI'],
    '小米': ['小米', 'MI', 'XIAOMI', '黑鲨', 'BLACKSHARK', 'SHARK'],
    'Apple': ['苹果', 'APPLE'],
    '三星': ['三星', 'SAMSUNG'],
    'OPPO': ['OPPO'],
    'NOKIA': ['诺基亚', 'NOKIA'],
    'Philips': ['飞利浦', 'PHILIPS'],
    '努比亚': ['努比亚', 'NUBIA'],
    '魅族': ['魅族', 'MEIZU'],
    'lenovo': ['联想', 'LENOVO'],
    '荣耀': ['荣耀', 'HONOR'],
    '中兴': ['中兴', 'ZTE', '守护宝'],
    'WE': ['WE'],
    'Smartisan': ['锤子', 'SMARTISAN'],
    '几觅': ['几觅'],
    'BlackBerry': ['黑莓', 'BLACKBERRY'],
    '酷派': ['酷派', 'COOPAD'],
    '天语': ['天语', 'K-TOUCH', 'KTOUCH'],
    '美图': ['美图', 'MEITU'],
    '360': ['360'],
    '一加': ['一加', 'ONEPLUS'],
}

cpu_brand_list = {
    '海思': ['海思', 'HISILICON'],
    '骁龙': ['骁龙', 'SANPDRAGON'],
    '联发科': ['联发科', 'MTK']
}

os_list = {
    'Android': ['安卓', 'ANDROID'],
    'IOS': ['IOS'],
}

etc_list = ['以官网信息为准', '--']


def change_etc(data):
    if data in etc_list:
        return '其他'
    return data


def delete_model_name(model, std_list):
    model = model.strip()
    for key, value in std_list.items():
        for v in value:
            re_v = re.compile(v, re.IGNORECASE)
            model = re_v.sub('', model).strip()
            if model.count('（') > 0:
                if model[0] == '（':
                    model = model[1:].strip()
                if model[0] == '）':
                    model = model[1:].strip()

    return model


def change_name(data, std_list):
    data = change_etc(data)
    if data == '其他':
        return data
    data_upper = data.upper()
    for key, value in std_list.items():
        for v in value:
            if v in data_upper:
                return key
    return data


def standardization():
    connect(DATABASE_NAME)
    products = Cellphone.objects.all()
    for product in products:
        product.brand = change_name(product.brand, cellphone_brand_list)
        product.model = delete_model_name(product.model, cellphone_brand_list)
        product.os = change_name(product.os, os_list)
        product.cpu = change_name(product.cpu, cpu_brand_list)
        product.save()


standardization()