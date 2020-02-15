import os

import web.configs


class LocalConfig(web.configs.BaseConfig):
    STORAGE_CLASS = 'web.storage.FileSystemStorage'
    STORAGE_CLASS_KWARGS = {'media_root': './media'}
    MESSAGE_CLASS = 'web.message.RedisMessage'
    MESSAGE_CLASS_KWARGS = {
        'host': os.environ['REDIS_HOST'],
        'port': os.environ['REDIS_PORT'],
        'db': int(os.environ['REDIS_DB']),
        'channel': os.environ['REDIS_CHANNEL'],
    }
    RESULT_MAX_WAITING_SECONDS = 3
