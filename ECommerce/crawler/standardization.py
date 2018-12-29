from app.models import *
from mongoengine import *
from ECommerce.settings import DATABASE_NAME

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

def change_brand_name(brand):
    brand_upper = brand.upper()
    for key, value in cellphone_brand_list.items():
        for v in value:
            if v in brand_upper:
                return key
    return brand


def standardization():
    connect(DATABASE_NAME)
    products = Cellphone.objects.all()
    for product in products:
        product.brand = change_brand_name(product.brand)
        product.save()


standardization()