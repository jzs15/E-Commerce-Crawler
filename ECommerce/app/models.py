from mongoengine import *


class Product(Document):
    title = StringField()
    model = StringField()
    shop_name = StringField()
    brand = StringField()
    platform = StringField()
    price = DecimalField()
    score = FloatField()
    comment_num = IntField()
    url = URLField(unique=True)
    date = StringField()
    image = StringField()

    meta = {
        'allow_inheritance': True,
    }


class Cellphone(Product):
    color = StringField()
    weight = StringField()
    thickness = StringField()
    width = StringField()
    height = StringField()
    os = StringField()
    cpu = StringField()
    ram = StringField()
    rom = StringField()
    frequency = StringField()
    screen_size = StringField()
    network_support = DictField()


class Refrigerator(Product):
    color = StringField()
    open_method = StringField()
    weather = StringField()
    VoltFre = StringField()
    rank = StringField()
    ability = StringField()
    method = StringField()
    dB = StringField()
    weight = StringField()
    cold_volume = StringField()
    ice_volume = StringField()
    form_size = StringField()
    case_size = StringField()


class Laptop(Product):
    color = StringField()
    os = StringField()
    core = StringField()
    cpu = StringField()
    ram = StringField()
    ssd = StringField()
    hdd = StringField()
    graphic_card = StringField()
    weight = StringField()
    frequency = StringField()


class Desktop(Product):
    color = StringField()
    os = StringField()
    core = StringField()
    cpu = StringField()
    ram = StringField()
    ssd = StringField()
    hdd = StringField()
    graphic_card = StringField()
    weight = StringField()


class Television(Product):
    tv_category = StringField()
    length = StringField()
    frequency = StringField()
    light = StringField()
    color = StringField()
    ratio = StringField()
    os = StringField()
    ram = StringField()
    rom = StringField()
    machine_power = StringField()
    wait_power = StringField()
    volt = StringField()
    size = StringField()
    weight = StringField()

