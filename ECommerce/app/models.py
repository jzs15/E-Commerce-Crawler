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
    url = URLField()
    date = StringField()
    image = StringField()

    meta = {
        'indexes': [
            {'fields': ('url'), 'unique': True},
        ],
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
    network = DictField()
    frequency = StringField()
    screen_size = StringField()
