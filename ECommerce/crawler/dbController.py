from app.models import *
from ECommerce.settings import DATABASE_NAME
from mongoengine import *

connect(DATABASE_NAME)
Desktop.objects.all().delete()