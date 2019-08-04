import io
import pathlib

import pytest

import web.pool
import web.server


samples_dir = pathlib.Path(__file__).parent / 'samples'


@pytest.fixture
def client():
    yield web.server.app.test_client()


@pytest.fixture
def pool():
    return web.pool.LatexPool()


@pytest.fixture
def latex_file():
    sample_path = samples_dir / 'hello.latex'
    return io.BytesIO(sample_path.read_bytes())


@pytest.fixture
def latex_zip():
    sample_path = samples_dir / 'multiple.zip'
    return './multiple/main.tex', io.BytesIO(sample_path.read_bytes())
