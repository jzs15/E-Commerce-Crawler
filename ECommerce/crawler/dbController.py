from app.models import *
from ECommerce.settings import DATABASE_NAME
from mongoengine import *

connect(DATABASE_NAME)
Laptop.objects.all().delete()