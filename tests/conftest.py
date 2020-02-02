import io
import pathlib

import pytest

import web


samples_dir = pathlib.Path(__file__).parent / 'samples'


@pytest.fixture
def app():
    return web.create_app()


@pytest.fixture(autouse=True)
def session(app):
    with app.app_context():
        app.db.create_all()
        yield app.db.session
        app.db.session.close()
        app.db.drop_all()


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def latex_file():
    sample_path = samples_dir / 'hello.latex'
    return io.BytesIO(sample_path.read_bytes())


@pytest.fixture
def latex_zip():
    sample_path = samples_dir / 'multiple.zip'
    return './multiple/main.tex', io.BytesIO(sample_path.read_bytes())
