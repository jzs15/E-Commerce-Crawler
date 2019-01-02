from ECommerce.settings import DATABASE_NAME
from mongoengine import *
from app.models import *
import json


def save_to_db(info, model):
    products = model.objects.filter(url=info['url'])
    if products.first() is None:
        product = model(**info)
        product.save()
    else:
        products.update(**info)


JSON_DATA = 'C:/Users/youkg/Desktop/json/'
connect(DATABASE_NAME)

with open(JSON_DATA + 'JD_Laptop.json', 'r') as json_file:
    data = json.load(fp=json_file)
    for datum in data:
        save_to_db(datum, Laptop)
