from app.models import *
from ECommerce.settings import DATABASE_NAME
from mongoengine import *
import json

connect(DATABASE_NAME)
with open('Desktop.json', 'r') as json_file:
    info = json.load(fp=json_file)
    print(type(info))