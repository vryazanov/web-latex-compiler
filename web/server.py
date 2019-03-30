import io

import flask
import latex


app = flask.Flask(__name__)


@app.route('/', methods=('get',))
def index():
    return flask.render_template('index.html')


@app.route('/upload', methods=('POST',))
def upload():
    _file = flask.request.files['file']
    pdf = latex.build_pdf(io.BytesIO(_file.stream.read()))
    return flask.Response(pdf.readb(), mimetype='application/pdf')
