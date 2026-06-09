import os

basedir = os.path.abspath(os.path.dirname(__file__))

secret_key = os.environ.get('SECRET_KEY')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')