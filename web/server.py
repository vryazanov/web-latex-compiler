import io

import flask
import latex

import web.pool


app = flask.Flask(__name__)
pool = web.pool.LatexPool()


@app.route('/', methods=('get',))
def index():
    return flask.render_template('index.html')


@app.route('/upload', methods=('POST',))
def upload():
    _file = flask.request.files['file']
    pdf = latex.build_pdf(io.BytesIO(_file.stream.read()))
    return flask.Response(pdf.readb(), mimetype='application/pdf')


@app.route('/upload-zip', methods=('POST',))
def upload_zip():
    # Process zip files here
    _file = flask.request.files['file']
    _bytes = io.BytesIO(_file.stream.read())
    return flask.jsonify({'result_id': pool.apply(_bytes)})


@app.route('/result/<result_id>', methods=('GET',))
def result(result_id):
    try:
        result = pool.get(result_id)
    except web.pool.NotFound:
        return '', 404
    except web.pool.NotReady:
        return '', 204
    return flask.Response(result.readb(), mimetype='application/pdf')
