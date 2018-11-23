from mongoengine import *


class Product(Document):
    title = StringField()
    product_name = StringField()
