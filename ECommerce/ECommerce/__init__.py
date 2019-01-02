from mongoengine import *
from .settings import DATABASE_NAME
from .celery import app as celery_app

print('Connect to database "{}"'.format(DATABASE_NAME))
connect(DATABASE_NAME)
