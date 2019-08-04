import io

import pytest

import web.server


@pytest.fixture
def client():
    yield web.server.app.test_client()


def test_upload(client):
    min_latex = (
        br"\documentclass{article}"
        br"\begin{document}"
        br"Hello, world!"
        br"\end{document}"
    )
    data = {
        'file': (io.BytesIO(min_latex), 'test.latex')
    }

    response = client.post(
        '/upload', data=data, content_type='multipart/form-data')

    assert response.data
