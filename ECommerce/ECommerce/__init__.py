from mongoengine import *
from .settings import DATABASE_NAME

print('Connect to database "{}"'.format(DATABASE_NAME))
connect(DATABASE_NAME)
