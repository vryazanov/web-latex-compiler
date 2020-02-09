import tempfile
import urllib.parse

import flask

import web.db


def index():
    return flask.render_template('index.html', upload=urllib.parse.urljoin(
        flask.request.url_root, '/upload'))


def upload():
    file_ = flask.request.files['file']

    async_result = web.db.AsyncResult()
    async_result.generate_origin_key(file_.filename)

    flask.current_app.db.session.add(async_result)
    flask.current_app.db.session.commit()

    flask.current_app.storage.put_object(async_result.origin_key, file_)
    flask.current_app.message.push({'async_result_id': async_result.id})

    return flask.Response(flask.url_for('result', token=async_result.token))


def result(token):
    async_result = web.db.AsyncResult.query.filter_by(
        token=token).one_or_none()

    if not async_result:
        return flask.Response('File is not found.', status=404)

    if not async_result.target_key:
        return flask.Response('File is not processed yet.', status=102)

    pdf = tempfile.TemporaryFile()
    flask.current_app.storage.get_object(
        async_result.target_key, pdf)
    pdf.seek(0)
    return flask.send_file(pdf, mimetype='application/pdf')
