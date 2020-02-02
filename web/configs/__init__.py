import os


class BaseConfig:
    ENV = 'production'
    DEBUG = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mb
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
