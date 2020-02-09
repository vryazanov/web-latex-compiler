import web.configs


class LocalConfig(web.configs.BaseConfig):
    STORAGE_CLASS = 'web.storage.FileSystemStorage'
    STORAGE_CLASS_KWARGS = {'media_root': './media'}
    MESSAGE_CLASS = 'web.message.LocalMessage'
    MESSAGE_CLASS_KWARGS = {}
    RESULT_MAX_WAITING_SECONDS = 3
