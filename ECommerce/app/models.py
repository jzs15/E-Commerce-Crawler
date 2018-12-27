from mongoengine import *


class Product(Document):
    title = StringField()
    model = StringField()
    shop_name = StringField()
    brand = StringField()
    platform = StringField()
    price = DecimalField()
    score = IntField()
    comment_num = FloatField()
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
    network_support = StringField()
