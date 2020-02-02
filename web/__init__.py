import os

import flask
import werkzeug.utils

import web.db
import web.storage
import web.views


def get_storage(config):
    storage_class = werkzeug.utils.import_string(config['STORAGE_CLASS'])
    return storage_class(**config['STORAGE_CLASS_KWARGS'])


def get_message(config):
    message_class = werkzeug.utils.import_string(config['MESSAGE_CLASS'])
    return message_class(**config['MESSAGE_CLASS_KWARGS'])


def create_app(config_path=os.environ['FLASK_CONFIG']):
    app = flask.Flask(__name__)
    app.config.from_object(config_path)

    app.db = web.db.db
    app.db.init_app(app)

    app.add_url_rule('/', 'index', web.views.index)
    app.add_url_rule('/upload', 'upload', web.views.upload, methods=('POST',))
    app.add_url_rule('/result/<token>', 'result', web.views.result)

    app.storage = get_storage(app.config)
    app.message = get_message(app.config)

    return app
