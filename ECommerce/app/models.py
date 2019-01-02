from mongoengine import *


class Product(Document):
    title = StringField(defalt='')
    model = StringField(defalt='')
    shop_name = StringField(defalt='')
    brand = StringField(defalt='')
    platform = StringField(defalt='')
    price = DecimalField()
    score = FloatField()
    comment_num = IntField()
    url = URLField(unique=True)
    date = StringField(defalt='')
    image = StringField(defalt='')

    meta = {
        'allow_inheritance': True,
    }


class Cellphone(Product):
    color = StringField(defalt='')
    weight = StringField(defalt='')
    thickness = StringField(defalt='')
    width = StringField(defalt='')
    height = StringField(defalt='')
    os = StringField(defalt='')
    cpu = StringField(defalt='')
    ram = StringField(defalt='')
    rom = StringField(defalt='')
    frequency = StringField(defalt='')
    screen_size = StringField(defalt='')
    network_support = DictField()


class Refrigerator(Product):
    color = StringField(defalt='')
    open_method = StringField(defalt='')
    weather = StringField(defalt='')
    voltFre = StringField(defalt='')
    rank = StringField(defalt='')
    ability = StringField(defalt='')
    method = StringField(defalt='')
    dB = StringField(defalt='')
    weight = StringField(defalt='')
    cold_volume = StringField(defalt='')
    ice_volume = StringField(defalt='')
    form_size = StringField(defalt='')
    case_size = StringField(defalt='')


class Laptop(Product):
    color = StringField(defalt='')
    os = StringField(defalt='')
    core = StringField(defalt='')
    cpu = StringField(defalt='')
    ram = StringField(defalt='')
    hdd = StringField(defalt='')
    ssd = StringField(defalt='')
    graphic_card = StringField(defalt='')
    weight = StringField(defalt='')
    frequency = StringField(defalt='')


class Desktop(Product):
    color = StringField(defalt='')
    os = StringField(defalt='')
    core = StringField(defalt='')
    cpu = StringField(defalt='')
    ram = StringField(defalt='')
    hdd = StringField(defalt='')
    ssd = StringField(defalt='')
    graphic_card = StringField(defalt='')
    weight = StringField(defalt='')


class Television(Product):
    tv_category = StringField(defalt='')
    length = StringField(defalt='')
    frequency = StringField(defalt='')
    light = StringField(defalt='')
    color = StringField(defalt='')
    ratio = StringField(defalt='')
    os = StringField(defalt='')
    ram = StringField(defalt='')
    rom = StringField(defalt='')
    machine_power = StringField(defalt='')
    wait_power = StringField(defalt='')
    volt = StringField(defalt='')
    size = StringField(defalt='')
    weight = StringField(defalt='')


class Washer(Product):
    color = StringField(defalt='')
    open_method = StringField(defalt='')
    drain_method = StringField(defalt='')
    weight = StringField(defalt='')
    wash_volume = StringField(defalt='')
    dewater_volume = StringField(defalt='')
    size = StringField(defalt='')
    rank = StringField(defalt='')