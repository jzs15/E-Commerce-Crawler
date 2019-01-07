from ECommerce.settings import DATABASE_NAME
from mongoengine import *
from app.models import *
import json
import sys


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


def main():
    with open(JSON_DATA + 'jd/Cellphone.json', 'r') as json_file:
        jd_c = json.load(fp=json_file)
    with open(JSON_DATA + 'sn/Cellphone.json', 'r') as json_file:
        sn_c = json.load(fp=json_file)
    with open(JSON_DATA + 'az/Cellphone.json', 'r') as json_file:
        az_c = json.load(fp=json_file)
    data = jd_c + sn_c + az_c
    for datum in data:
        save_to_db(datum, Cellphone)

    with open(JSON_DATA + 'jd/Washer.json', 'r') as json_file:
        jd_w = json.load(fp=json_file)
    with open(JSON_DATA + 'sn/Washer.json', 'r') as json_file:
        sn_w = json.load(fp=json_file)
    data = jd_w + sn_w
    for datum in data:
        save_to_db(datum, Washer)

    with open(JSON_DATA + 'jd/Desktop.json', 'r') as json_file:
        data = json.load(fp=json_file)
    for datum in data:
        save_to_db(datum, Desktop)

    with open(JSON_DATA + 'jd/Laptop.json', 'r') as json_file:
        data = json.load(fp=json_file)
    for datum in data:
        save_to_db(datum, Laptop)

    with open(JSON_DATA + 'jd/Refrigerator.json', 'r') as json_file:
        data = json.load(fp=json_file)
    for datum in data:
        save_to_db(datum, Refrigerator)

    with open(JSON_DATA + 'jd/Television.json', 'r') as json_file:
        data = json.load(fp=json_file)
    for datum in data:
        save_to_db(datum, Television)


if __name__ == '__main__':
    sys.exit(main())

