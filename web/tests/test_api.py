import io

import pytest

from back import server


@pytest.fixture
def client():
    yield server.app.test_client()


def test_upload(client):
    data = {'entry': ''}
    min_latex = (b"\documentclass{article}"
                 b"\\begin{document}"
                 b"Hello, world!"
                 b"\end{document}")
    data['file'] = (io.BytesIO(min_latex), 'test.latex')

    response = client.post(
        '/upload', data=data, content_type='multipart/form-data')

    print('upload?', dir(response), response.is_streamed, dir(response.stream))
    print(response.data)
