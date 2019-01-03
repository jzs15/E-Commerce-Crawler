from ECommerce.settings import DATABASE_NAME
from mongoengine import *
from app.models import *
import json


def save_to_db(info, model):
    products = model.objects.filter(url=info['url'])
    if products.first() is None:
        product = model(**info)
        try:
            product.save()
        except NotUniqueError:
            print('NotUnique')
            pass


JSON_DATA = 'json_data/'
connect(DATABASE_NAME)

with open(JSON_DATA + 'Washer.json', 'r') as json_file:
    data = json.load(fp=json_file)
    for datum in data:
        save_to_db(datum, Washer)
