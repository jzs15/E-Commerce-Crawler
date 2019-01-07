from app.models import *
from mongoengine import *
from ECommerce.settings import DATABASE_NAME
import re
import sys

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
    'Android': ['安卓', 'ANDROID', 'ANDRIOD'],
    'IOS': ['IOS'],
    'YIUI': ['YIUI', '易柚'],
    'FunUI': ['FUNUI'],
    '酷开': ['酷开'],
    'AI OS': ['AI OS'],
    '其他': ['0', '-', '咨询客服'],
    'MIUI': ['MI'],
}

computer_os = ['家庭版', '家庭中文版', '中文版', '专业版', '家庭普通版', '试用版', '正版']

etc_list = ['以官网信息为准', '以官方信息为准', '--']


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
    if model:
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
    return data.strip()


def change_weather(weather):
    if weather == '其他' or weather == '其它':
        return '其他'
    if re.match('[^a-zA-Z]*([a-zA-Z]+)', weather) is None:
        return weather
    wth = ""
    if 'N' in weather:
        if weather[weather.find('N') - 1] != 'S':
            wth += "温带型"
    if 'T' in weather:
        if weather[weather.find('T') - 1] != 'S':
            wth += "热带型" if len(wth) == 0 else "/热带型"
    if 'SN' in weather:
        wth += "亚温带型" if len(wth) == 0 else "/亚温带型"
    if 'ST' in weather:
        wth += "亚热带型" if len(wth) == 0 else "/亚热带型"
    return wth


def remove_bracket(model):
    model = model.replace('（', '(', model.count('（'))
    model = model.replace('）', ')', model.count('）'))
    num = model.count('(')
    for i in range(num):
        index1 = model.find('(')
        index2 = model.find(')')
        model = model[:index1] + model[index2 + 1:]
    return model


def change_os(os):
    for i in computer_os:
        if i in os:
            index = os.find(i)
            os = os[:index] + os[index + len(i):]
            os = os.strip()
    if 'Win' in os and 'Windows' not in os:
        index = os.find('Win')
        os = os[:index] + 'Windows' + os[index + 3:]
    os = os.replace(' ', '', os.count(' '))
    return os


def standardization():
    connect(DATABASE_NAME)
    products = Cellphone.objects.all()
    for product in products:
        product.brand = change_name(product.brand, cellphone_brand_list)
        product.brand = remove_bracket(product.brand)
        product.model = delete_model_name(product.model, cellphone_brand_list)
        product.os = change_name(product.os, os_list)
        product.cpu = change_name(product.cpu, cpu_brand_list)
        product.cpu = remove_bracket(product.cpu)
        product.save()

    products = Refrigerator.objects.all()
    for product in products:
        product.brand = remove_bracket(product.brand)
        product.rank = product.rank.replace(' ', '', product.rank.count(' '))
        product.weather = change_weather(product.weather)
        product.method = remove_bracket(product.method)
        product.save()

    products = Washer.objects.all()
    for product in products:
        product.brand = remove_bracket(product.brand)
        product.rank = product.rank.replace(' ', '', product.rank.count(' '))
        product.save()

    products = Laptop.objects.all()
    for product in products:
        product.brand = remove_bracket(product.brand)
        product.os = change_os(product.os)
        product.save()

    products = Desktop.objects.all()
    for product in products:
        product.brand = remove_bracket(product.brand)
        product.os = change_os(product.os)
        product.save()

    products = Television.objects.all()
    for product in products:
        product.brand = remove_bracket(product.brand)
        product.os = change_name(product.os, os_list)
        product.save()


if __name__ == '__main__':
    sys.exit(standardization())
