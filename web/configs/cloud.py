import os

import web.configs


class CloudConfig(web.configs.BaseConfig):
    STORAGE_CLASS = 'web.storage.CloudStorage'
    MESSAGE_CLASS = 'web.message.CloudMessage'

    MESSAGE_CLASS_KWARGS = {
        'project': os.environ['GC_PROJECT'],
        'topic': os.environ['GC_TOPIC'],
        'subscription': os.environ['GC_SUBSCRIPTION'],
    }
    STORAGE_CLASS_KWARGS = {
        'bucket_name': os.environ['GC_STORAGE'],
    }
