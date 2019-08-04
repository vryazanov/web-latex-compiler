import io

import flask

import web.pool


app = flask.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mb

pool = web.pool.LatexPool()


@app.route('/', methods=('get',))
def index():
    return flask.render_template('index.html')


@app.route('/upload', methods=('POST',))
def upload():
    _file = flask.request.files['file']
    pdf = pool.apply(io.BytesIO(_file.stream.read()))
    return flask.Response(pdf.readb(), mimetype='application/pdf')


@app.route('/upload-zip', methods=('POST',))
def upload_zip():
    entry = flask.request.form['entry']
    bytes_ = flask.request.files['file'].stream.read()
    result_id = pool.apply_zip(entry, io.BytesIO(bytes_))
    return flask.jsonify({'result_id': result_id})


@app.route('/result/<result_id>', methods=('GET',))
def result(result_id):
    try:
        result = pool.get(result_id)
    except web.pool.NotFound:
        return '', 404
    except web.pool.NotReady:
        return '', 204
    return flask.Response(result.readb(), mimetype='application/pdf')
