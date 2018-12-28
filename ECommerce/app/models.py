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
